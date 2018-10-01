<template>
  <div class="svgbox">
    <div id="svg-wrapper" v-html="svgContent">
    </div>
    <div id="svgOption" class="overlay">
      <span class="button" v-on:click="panZoom ? panZoom.zoomIn() : ''"><i class="fa fa-search-plus"></i></span>
      <span class="button" v-on:click="panZoom ? panZoom.zoomOut(): ''"><i class="fa fa-search-minus"></i></span>
      <span class="button" v-on:click="svgfit()"><i class="fa fa-arrows-alt"></i></span>
    </div>
    <div id="svgSearch" class="overlay">
      <div><span id="st">Search:</span></div>
      <div class="control" :class="{ 'is-loading' : isLoadingSearch }">
        <input id="searchInput" class="input"
        type="text" 
        :class="searchInputClass"
        v-model.trim="searchTerm"
        v-on:keyup.enter="searchComponentIDs(searchTerm)" :disabled="!loadedMap"/>
      </div>
      <div v-show="searchTerm && totalSearchMatch">
        <span id="searchResCount"><input type="text" v-model="searchResultCountText" readonly disabled /></span>
        <span class="button has-text-dark" @click="searchPrevElementOnSVG"><i class="fa fa-angle-left"></i></span>
        <span class="button has-text-dark" @click="searchNextElementOnSVG"><i class="fa fa-angle-right"></i></span>
        <span class="button has-text-dark" @click="highlightElementsFound">Highlight all</span>
      </div>
    </div>
  </div>
</template>

<script>

import $ from 'jquery';
import axios from 'axios';
import svgPanZoom from 'svg-pan-zoom';
import Loader from 'components/Loader';
import { default as EventBus } from '../../../event-bus';
import { getExpressionColor } from '../../../expression-sources/hpa';

export default {
  name: 'svgmap',
  props: ['model'],
  components: {
    Loader,
  },
  data() {
    return {
      errorMessage: '',
      loadedMap: null,
      loadedMapType: null,
      loadedMapHistory: {},
      svgContent: null,
      svgContentHistory: {},
      svgName: '',
      svgBigMapName: 'whole_metabolic_network_without_details',
      panZoom: null,

      ids: [],
      elmFound: [],
      elmsHL: [],
      // TODO handle multi model history
      selectedItemHistory: {},

      HPARNAlevelsHistory: {},
      enzymeRNAlevels: {}, // enz id as key, current tissue level as value

      searchTerm: '',
      searchInputClass: '',
      isLoadingSearch: false,

      currentSearchMatch: 0,
      totalSearchMatch: 0,

      zoomBox: {
        minX: 99999,
        maxX: 0,
        minY: 99999,
        maxY: 0,
        centerX: 0,
        centerY: 0,
        h: 0,
        w: 0,
      },
      maxZoomLvl: 0.65,
      labelZoomLvl: 0.40,
      nodeZoomLvl: 0.15,
      allowZoom: true,
      dragging: false,

      svgMapURL: `${window.location.origin}/svgs`, // SEDME
    };
  },
  computed: {
    searchResultCountText() {
      return `${this.currentSearchMatch}/${this.totalSearchMatch}`;
    },
  },
  watch: {
    searchTerm() {
      if (!this.searchTerm) {
        this.unHighlight();
        this.totalSearchMatch = 0;
        this.searchInputClass = 'is-info';
      }
    },
  },
  created() {
    EventBus.$off('showSVGmap');
    EventBus.$off('loadHPARNAlevels');

    EventBus.$on('showSVGmap', (type, name, ids, forceReload) => {
      // console.log(`emit showSVGmap ${type} ${name} ${ids} ${forceReload}`);
      if (forceReload) {
        this.svgName = '';
      }
      // set the type, even if might fail to load the map?
      this.loadedMapType = type;
      if (type === 'compartment' || type === 'subsystem') {
        this.showMap(name);
      } else if (type === 'find') {
        this.hlElements(name, ids);
      } else if (!this.svgName || type === 'wholemap') {
        this.loadSVG('wholemap', null);
      }
    });

    EventBus.$on('loadHPARNAlevels', (tissue) => {
      this.loadHPAlevelsOnMap(tissue);
    });
  },
  mounted() {
    const self = this;
    $('#svg-wrapper').on('mousedown', 'svg', () => {
      self.isDragging = false;
    })
    .on('mousemove', 'svg', () => {
      self.isDragging = true;
    })
    .on('mouseup', 'svg', (e) => {
      if (!self.isDragging) {
        const target = $(e.target);
        if (!target.hasClass('.met') && !target.hasClass('.enz') && !target.hasClass('.rea')) {
          self.unSelectElement();
        }
      }
      self.isDragging = false;
    });
    $('#svg-wrapper').on('click', '.met', function f() {
      // exact the real id from the id
      const id = $(this).attr('id').split('-')[0].trim();
      self.selectElement(id, 'metabolite');
    });
    $('#svg-wrapper').on('click', '.enz', function f() {
      // exact the real id from the id
      const id = $(this).attr('id').split('-')[0].trim();
      self.selectElement(id, 'enzyme');
    });
    $('#svg-wrapper').on('click', '.rea', function f() {
      const id = $(this).attr('id');
      self.selectElement(id, 'reaction');
    });
  },
  methods: {
    loadSvgPanZoom(callback) {
      // load the lib svgPanZoom on the SVG loaded
      setTimeout(() => {
        this.panZoom = svgPanZoom('#svg-wrapper svg', {
          zoomEnabled: true,
          controlIconsEnabled: false,
          minZoom: 0.5,
          maxZoom: 30,
          zoomScaleSensitivity: 0.2,
          fit: true,
          beforeZoom: (oldzl, newzl) => {
            const rzl = this.panZoom.getSizes().realZoom;
            if (oldzl < newzl && rzl > this.maxZoomLvl + 0.01) {
              this.allowZoom = false;
              return false;
            }
            return true;
          },
          beforePan: () => {
            if (!this.allowZoom) {
              this.allowZoom = true;
              return false;
            }
            return true;
          },
          onZoom: () => {
            const rzl = this.panZoom.getSizes().realZoom;
            if (rzl >= this.labelZoomLvl) {
              $('.met .lbl, .rea .lbl, .enz .lbl').attr('display', 'inline');
            } else {
              $('.met .lbl, .rea .lbl, .enz .lbl').attr('display', 'none');
            }
            if (rzl >= this.nodeZoomLvl) {
              $('.met, .rea, .enz, .fe, .ee').attr('display', 'inline');
            } else {
              $('.met, .rea, .enz, .fe, .ee').attr('display', 'none');
            }
          },
        });
        this.svgfit();
        this.unHighlight();
        if (callback) {
          // call findElementsOnSVG
          callback();
        } else {
          this.$emit('loadComplete', true, '');
        }
      }, 0);
    },
    svgfit() {
      $('#svg-wrapper svg').attr('width', '100%');
      const vph = $('.svgbox').first().innerHeight();
      // console.log('vph', vph);

      $('#svg-wrapper svg').attr('height', `${vph}px`);
      if (this.panZoom) {
        this.panZoom.resize(); // update SVG cached size
        this.panZoom.fit();
        this.panZoom.center();
        this.panZoom.zoomOut(); // tmp fix for iacurate fitting
      }
    },
    loadSVG(id, callback) {
      // load the svg file from the server
      this.$emit('loading');
      // reset some values
      this.searchTerm = '';
      this.totalSearchMatch = 0;
      this.searchInputClass = 'is-info';

      // if already loaded, just call the callback funtion
      let currentLoad = this.$parent.compartmentsSVG[id];
      if (!currentLoad) {
        currentLoad = this.$parent.subsystemsSVG[id];
        if (!currentLoad) {
          this.loadedMapType = null;
          this.$emit('loadComplete', false, '');
          return;
        }
      }
      const newSvgName = currentLoad.filename;
      if (!newSvgName) {
        // TODO remove this when all svg files are available
        this.$emit('loadComplete', false, 'SVG map not available.');
        return;
      }

      if (newSvgName !== this.svgName) {
        if (newSvgName in this.loadedMapHistory) {
          this.svgContent = this.svgContentHistory[newSvgName];
          this.loadedMap = this.loadedMapHistory[newSvgName];
          this.svgName = newSvgName;
          setTimeout(() => {
            this.loadSvgPanZoom(callback);
          }, 0);
        } else {
          const svgLink = `${this.svgMapURL}/${this.model}/${newSvgName}`;
          axios.get(svgLink)
            .then((response) => {
              this.svgContent = response.data;
              this.svgName = newSvgName;
              this.loadedMap = currentLoad;
              this.svgContentHistory[this.svgName] = response.data;
              this.loadedMapHistory[this.svgName] = currentLoad;
              setTimeout(() => {
                // this.showLoader = false;
                this.loadSvgPanZoom(callback);
              }, 0);
            })
            .catch(() => {
              // TODO: handle error
              this.$emit('loadComplete', false, 'SVG map not available.');
            });
        }
      } else if (callback) {
        this.loadedMap = currentLoad;
        // call findElementsOnSVG
        callback();
      } else {
        this.loadedMap = currentLoad;
        this.svgfit();
        this.$emit('loadComplete', true, '');
      }
    },
    loadHPAlevelsOnMap(tissue) {
      if (this.svgName in this.HPARNAlevelsHistory) {
        this.readHPARNAlevels(tissue);
        return;
      }
      axios.get(`${this.model}/enzymes/hpa_rna_levels/${this.loadedMap.name_id}`)
      .then((response) => {
        this.HPARNAlevelsHistory[this.svgName] = response.data;
        setTimeout(() => {
          this.readHPARNAlevels(tissue);
        }, 0);
      })
      .catch(() => {
        EventBus.$emit('loadRNAComplete', false, '');
        return;
      });
    },
    readHPARNAlevels(tissue) {
      if (tissue === 'None') {
        $('#svg-wrapper .enz .shape').attr('fill', '#fa0');
        this.enzymeRNAlevels = {};
        return;
      }
      const index = this.HPARNAlevelsHistory[this.svgName].tissues.indexOf(tissue);
      if (index === -1) {
        EventBus.$emit('loadRNAComplete', false, '');
        return;
      }
      const levels = this.HPARNAlevelsHistory[this.svgName].levels;
      $('#svg-wrapper .enz .shape').attr('fill', 'whitesmoke'); // init to NA
      for (const array of levels) {
        const enzID = array[0];
        let level = Math.log2(parseFloat(array[1].split(',')[index]) + 1);
        level = Math.round((level + 0.00001) * 100) / 100;
        this.enzymeRNAlevels[enzID] = level;
        const classs = `#svg-wrapper .enz.${enzID} .shape`;
        $(classs).attr('fill', getExpressionColor(level));
      }
      // update cached selected elements
      for (const id of Object.keys(this.selectedItemHistory)) {
        if (this.enzymeRNAlevels[id]) {
          this.selectedItemHistory[id].rnaLvl = this.enzymeRNAlevels[id];
        }
      }
      EventBus.$emit('loadRNAComplete', true, '');
    },
    searchComponentIDs(term) {
      // get the correct IDs from the backend
      if (!this.searchTerm) {
        this.searchInputClass = 'is-warning';
        return;
      }
      this.isLoadingSearch = true;
      axios.get(`${this.model}/search_map/${this.loadedMapType}/${this.loadedMap.name_id}/${term}`)
      .then((response) => {
        this.searchInputClass = 'is-success';
        this.ids = response.data;
        this.findElementsOnSVG();
        this.resetZoombox();
        setTimeout(() => {
          if (this.elmFound.length !== 0) {
            this.currentSearchMatch = 1;
            this.updateZoomBox(this.elmFound[0]);
          }
        }, 0);
      })
      .catch((error) => {
        this.isLoadingSearch = false;
        const status = error.status || error.response.status;
        if (status !== 404) {
          this.$emit('loadComplete', false, 'An error occurred. Please try again later.');
          this.searchInputClass = 'is-info';
        } else {
          this.searchInputClass = 'is-danger';
        }
        return;
      });
    },
    findElementsOnSVG() {
      if (!this.ids) {
        return;
      }
      this.elmFound = [];
      for (let i = 0; i < this.ids.length; i += 1) {
        const id = this.ids[i].trim();
        const idname = `#svg-wrapper #${id}, #svg-wrapper .rea.${id}, #svg-wrapper .met.${id}, #svg-wrapper .enz.${id}`;
        const elms = $(idname);
        this.totalSearchMatch = elms.length;
        this.currentSearchMatch = 0;
        for (let j = 0; j < elms.length; j += 1) {
          this.elmFound.push(elms[j]);
        }
      }
      this.isLoadingSearch = false;
    },
    searchNextElementOnSVG() {
      if (this.totalSearchMatch <= 1) {
        return;
      }
      this.currentSearchMatch += 1;
      if (this.currentSearchMatch > this.totalSearchMatch) {
        this.currentSearchMatch = 1;
      }
      this.resetZoombox();
      this.updateZoomBox(this.elmFound[this.currentSearchMatch - 1]);
    },
    searchPrevElementOnSVG() {
      if (this.totalSearchMatch <= 1) {
        return;
      }
      this.currentSearchMatch -= 1;
      if (this.currentSearchMatch < 1) {
        this.currentSearchMatch = this.totalSearchMatch;
      }
      this.resetZoombox();
      this.updateZoomBox(this.elmFound[this.currentSearchMatch - 1]);
    },
    updateZoomBoxCoor(coordinate) {
      this.zoomBox.minX = coordinate.minX;
      this.zoomBox.maxX = coordinate.maxX;
      this.zoomBox.minY = coordinate.minY;
      this.zoomBox.maxY = coordinate.maxY;
    },
    updateZoomBox(el) {
      /* eslint-disable no-param-reassign */
      const s = $(el).find('.shape')[0];
      let t = this.getTransform(el);
      if (!t) {
        t = this.getTransform(s);
      }
      const x = t[4];
      const y = t[5];
      const oldDisplay = el.style.display;
      el.style.display = 'block';
      const w = s.getBBox().width;
      const h = s.getBBox().height;
      el.style.display = oldDisplay;
      if (x < this.zoomBox.minX) {
        this.zoomBox.minX = x;
      }
      if (x + w > this.zoomBox.maxX) {
        this.zoomBox.maxX = x + w;
      }
      if (y < this.zoomBox.minY) {
        this.zoomBox.minY = y;
      }
      if (y + h > this.zoomBox.maxY) {
        this.zoomBox.maxY = y + h;
      }
      this.zoomBox.w = this.zoomBox.maxX - this.zoomBox.minX;
      this.zoomBox.h = this.zoomBox.maxY - this.zoomBox.minY;
      this.zoomOnBox();
    },
    resetZoombox() {
      this.zoomBox = {
        minX: 99999,
        maxX: 0,
        minY: 99999,
        maxY: 0,
        centerX: 0,
        centerY: 0,
        h: 0,
        w: 0,
      };
    },
    getCenterZoombox() {
      this.zoomBox.w = this.zoomBox.maxX - this.zoomBox.minX;
      this.zoomBox.h = this.zoomBox.maxY - this.zoomBox.minY;
      this.zoomBox.centerX = this.zoomBox.minX + (this.zoomBox.w / 2.0);
      this.zoomBox.centerY = this.zoomBox.minY + (this.zoomBox.h / 2.0);
    },
    getTransform(el) {
      // read and parse the transform attribut
      let transform = el.getAttribute('transform');
      if (transform) {
        transform = transform.substring(0, transform.length - 1);
        transform = transform.substring(7, transform.length);
        return transform.split(',').map(parseFloat);
      }
      return null;
    },
    highlightElementsFound() {
      this.unHighlight();
      this.elmHL = [];
      for (const el of this.elmFound) {
        $(el).addClass('hl');
        this.elmHL.push(el);
      }
    },
    unHighlight() {
      if (this.elmHL) {
        // un-highlight elements
        for (let i = 0; i < this.elmHL.length; i += 1) {
          $(this.elmHL[i]).removeClass('hl');
        }
        this.elmHL = [];
      }
    },
    zoomOnBox() {
      this.getCenterZoombox();
      const realZoom = this.panZoom.getSizes().realZoom;
      this.panZoom.pan({
        x: -(this.zoomBox.centerX * realZoom) + (this.panZoom.getSizes().width / 2),
        y: -(this.zoomBox.centerY * realZoom) + (this.panZoom.getSizes().height / 2),
      });
      const viewBox = this.panZoom.getSizes().viewBox;
      let newScale = Math.min(viewBox.width / this.zoomBox.w, viewBox.height / this.zoomBox.h);
      const maxZoomLvl = (this.maxZoomLvl * this.panZoom.getZoom()) / realZoom;
      if (newScale > maxZoomLvl) {
        newScale = maxZoomLvl + 0.01;
      }
      this.panZoom.zoom(newScale);
    },
    showMap(id) {
      if (id) {
        // const compartment = getCompartmentFromName(compartmentName);
        this.loadSVG(id, null);
      }
    },
    selectElement(id, type) {
      if (this.selectedItemHistory[id]) {
        EventBus.$emit('updatePanelSelectionData', this.selectedItemHistory[id]);
        return;
      }
      EventBus.$emit('startSelectedElement');
      axios.get(`${this.model}/${type}s/${id}`)
      .then((response) => {
        let data = response.data;
        if (type === 'reaction') {
          data = data.reaction;
        } else if (type === 'enzyme') {
          // add the RNA level if any
          if (id in this.enzymeRNAlevels) {
            data.rnaLvl = this.enzymeRNAlevels[id];
          }
        }
        data.type = type;
        EventBus.$emit('updatePanelSelectionData', data);
        this.selectedItemHistory[id] = data;
        EventBus.$emit('endSelectedElement', true);
      })
      .catch(() => {
        EventBus.$emit('endSelectedElement', false);
      });
    },
    unSelectElement() {
      EventBus.$emit('unSelectedElement');
    },
  },
};
</script>

<style lang="scss">
  .met, .rea, .enz {
    .shape, .lbl {
      cursor: pointer;
    }
    &:hover {
      .shape {
        fill: red;
        stroke-width: 3px;
      }
      .lbl {
        font-weight: 900;
        text-shadow: 0 0 2px white;
      }
    }
  }

  .svgbox {
    position: relative;
    margin: 0;
    padding: 0;
    width: 100%;
    height:100%;
  }

  #svgOption {
    position: absolute;
    top: 2.25rem;
    left: 2.25rem;
    span:not(:last-child) {
      display: inline-block;
      margin-right: 5px;
    }
  }

  #svgSearch {
    top: 2.25rem;
    left: 25%;
    margin: 0;
    padding: 15px;
    div {
      display: inline-block;
      vertical-align: middle;
    }
    #st {
      display: inline-block;
      margin-right: 5px;
    }
    span:first-child {
      color: white;
    }
    #searchInput {
      display: inline-block;
      margin-right: 5px;
      width: 30vw;
    }
    #searchResCount {
      input {
        width: 60px;
        text-align: center;
      }
    }
  }

  svg .hl {
    display: inline;
    .shape {
      fill: red;
      stroke: orange;
      stroke-width: 3;
      display: inline;
    }
  }

</style>
