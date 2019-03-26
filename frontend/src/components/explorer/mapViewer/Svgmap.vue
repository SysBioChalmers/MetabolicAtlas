<template>
  <div class="svgbox">
    <div id="svg-wrapper" v-html="svgContent">
    </div>
    <div id="svgOption" class="overlay">
      <span class="button" v-on:click="zoomOut(false)" title="Zoom in"><i class="fa fa-search-plus"></i></span>
      <span class="button" v-on:click="zoomOut(true)" title="Zoom out"><i class="fa fa-search-minus"></i></span>
      <span class="button" v-on:click="toggleGenes()" title="Show/Hide genes"><i class="fa fa-filter"></i></span>
    </div>
    <div id="svgSearch" class="overlay">
      <div class="control" :class="{ 'is-loading' : isLoadingSearch }">
        <input id="searchInput" title="Exact search by id, name, alias. Press Enter for results"
          class="input" type="text" :class="searchInputClass" v-model.trim="searchTerm"
          v-on:keyup.enter="searchComponentIDs(searchTerm)" :disabled="!loadedMap"
          placeholder="Exact search by id, name, alias"/>
      </div>
      <div v-show="searchTerm && totalSearchMatch">
        <span id="searchResCount" class="button has-text-dark" @click="centerElementOnSVG(0)" title="Click to center on current match">
          {{ this.currentSearchMatch }} of {{this.totalSearchMatch }}
        </span>
        <span class="button has-text-dark" @click="centerElementOnSVG(-1)" title="Go to previous"><i class="fa fa-angle-left"></i></span>
        <span class="button has-text-dark" @click="centerElementOnSVG(1)" title="Go to next"><i class="fa fa-angle-right"></i></span>
        <span class="button has-text-dark" @click="highlightElementsFound" title="Highlight all matches">Highlight all</span>
      </div>
    </div>
    <div id="tooltip" ref="tooltip"></div>
  </div>
</template>

<script>

import axios from 'axios';
import $ from 'jquery';
import JQPanZoom from 'jquery.panzoom';
import JQMouseWheel from 'jquery-mousewheel';
import Loader from 'components/Loader';
import { default as EventBus } from '../../../event-bus';
import { getExpressionColor } from '../../../expression-sources/hpa';
import { default as messages } from '../../../helpers/messages';

// hack: the only way for jquery plugins to play nice with the plugins inside Vue
$.Panzoom = JQPanZoom;
$.fn.extend({
  mousewheel: function fn(options) {
    return this.each(function f() { return JQMouseWheel.mousewheel(this, options); });
  },
  unmousewheel: function fn() {
    return this.each(function f() { return JQMouseWheel.unmousewheel(this); });
  },
});


export default {
  name: 'svgmap',
  props: ['model', 'mapsData'],
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

      $panzoom: null,
      panzoomOptions: {
        maxScale: 1,
        minScale: 0.03,
        increment: 0.02,
        animate: false,
        linearZoom: true,
      },
      currentZoomScale: 1,

      idsFound: [],
      elmFound: [],
      elmsHL: [],
      // TODO handle multi model history
      selectedItemHistory: {},
      selectElementID: null,

      HPARNAlevelsHistory: {},
      enzymeRNAlevels: {}, // enz id as key, current tissue level as value

      searchTerm: '',
      searchInputClass: '',
      isLoadingSearch: false,

      currentSearchMatch: 0,
      totalSearchMatch: 0,

      svgMapURL: `${window.location.origin}/svgs`, // SEDME
    };
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
      if (forceReload) {
        this.svgName = '';
      }
      // set the type, even if might fail to load the map?
      this.loadedMapType = type;
      if (type === 'compartment' || type === 'subsystem') {
        if (name) {
          this.idsFound = ids;
          const callback = ids.length !== 0 ? this.findElementsOnSVG : null;
          this.loadSVG(name, callback);
        }
      } else if (type === 'find') {
        this.hlElements(name, ids);
      }
    });

    EventBus.$on('loadHPARNAlevels', (tissue) => {
      this.loadHPAlevelsOnMap(tissue);
    });
  },
  mounted() {
    const self = this;
    for (const aClass of ['.met', '.enz', '.rea', '.subsystem']) {
      $('#svg-wrapper').on('click', aClass, function f() {
        self.selectElement($(this));
      });
    }
    $('#svg-wrapper').on('mouseover', '.enz', function f(e) {
      const id = $(this).attr('class').split(' ')[1].trim();
      if (id in self.enzymeRNAlevels) {
        self.$refs.tooltip.innerHTML = `RNA level: ${self.enzymeRNAlevels[id]}`;
        self.$refs.tooltip.style.top = `${(e.pageY - $('.svgbox').first().offset().top) + 15}px`;
        self.$refs.tooltip.style.left = `${(e.pageX - $('.svgbox').first().offset().left) + 15}px`;
        self.$refs.tooltip.style.display = 'block';
      }
    });
    $('#svg-wrapper').on('mouseout', '.enz', () => {
      self.$refs.tooltip.innerHTML = '';
      self.$refs.tooltip.style.display = 'none';
    });
  },
  methods: {
    toggleGenes() {
      if ($('.enz, .ee').first().attr('visibility') === 'hidden') {
        $('.enz, .ee').attr('visibility', 'visible');
      } else {
        $('.enz, .ee').attr('visibility', 'hidden');
      }
    },
    zoomOut(bool) {
      if (this.$panzoom) {
        this.$panzoom.panzoom('zoom', bool, {
          focal: {
            clientX: this.clientFocusX(),
            clientY: this.clientFocusY(),
          },
        });
      }
    },
    loadSvgPanZoom(callback) {
      // load the lib svgPanZoom on the SVG loaded
      if (!this.$panzoom) {
        this.$panzoom = $('#svg-wrapper').panzoom(this.panzoomOptions);
      } else {
        this.$panzoom = $('#svg-wrapper').panzoom('reset', this.panzoomOptions);
      }
      setTimeout(() => {
        const minZoomScale = $('.svgbox').width() / $('#svg-wrapper svg').width();
        const focusX = ($('#svg-wrapper svg').width() / 2) - ($('.svgbox').width() / 2);
        const focusY = ($('#svg-wrapper svg').height() / 2) - ($('.svgbox').height() / 2);
        this.$panzoom.panzoom('pan', -focusX, -focusY);
        this.$panzoom.panzoom('zoom', true, {
          increment: 1 - minZoomScale,
          focal: {
            clientX: this.clientFocusX(),
            clientY: this.clientFocusY(),
          },
        });
        this.$panzoom.on('mousewheel.focal', (e) => {
          e.preventDefault();
          const delta = e.delta || e.originalEvent.wheelDelta;
          const zoomOut = delta ? delta < 0 : e.originalEvent.deltaY > 0;
          this.$panzoom.panzoom('zoom', zoomOut, { focal: e });
        });
        this.$panzoom.on('panzoomzoom', (e, panzoom, scale) => { // ignored opts param
          this.currentZoomScale = scale;
        });
        this.unHighlight();
        if (callback) {
          if (callback === this.findElementsOnSVG) {
            callback(true);
            this.$emit('loadComplete', true, '');
          }
        } else {
          this.$emit('loadComplete', true, '');
        }
      }, 0);
    },
    loadSVG(id, callback) {
      // load the svg file from the server
      this.$emit('loading');
      // reset some values
      this.searchTerm = '';
      let mapInfo = this.mapsData.compartments[id];
      if (!mapInfo) {
        mapInfo = this.mapsData.subsystems[id];
        if (!mapInfo) {
          this.loadedMapType = null;
          this.$emit('loadComplete', false, '');
          return;
        }
      }
      const newSvgName = mapInfo.filename;
      if (!newSvgName) {
        this.$emit('loadComplete', false, messages.mapNotFound);
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
          const svgLink = `${this.svgMapURL}/${this.model.database_name}/${newSvgName}`;
          axios.get(svgLink)
            .then((response) => {
              this.svgContent = response.data;
              this.svgName = newSvgName;
              this.loadedMap = mapInfo;
              this.svgContentHistory[this.svgName] = response.data;
              this.loadedMapHistory[this.svgName] = mapInfo;
              setTimeout(() => {
                // this.showLoader = false;
                this.loadSvgPanZoom(callback);
              }, 0);
            })
            .catch(() => {
              this.$emit('loadComplete', false, messages.mapNotFound);
            });
        }
      } else {
        this.loadedMap = mapInfo;
        // if already loaded, just call the callback funtion
        if (callback) {
          callback();
        }
        this.$emit('loadComplete', true, '');
      }
    },
    loadHPAlevelsOnMap(tissue) {
      if (this.svgName in this.HPARNAlevelsHistory) {
        this.readHPARNAlevels(tissue);
        return;
      }
      axios.get(`${this.model.database_name}/enzyme/hpa_rna_levels/${this.loadedMap.name_id}`)
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
      axios.get(`${this.model.database_name}/search_map/${this.loadedMapType}/${this.loadedMap.name_id}/${term}`)
      .then((response) => {
        this.searchInputClass = 'is-success';
        this.idsFound = response.data;
        this.findElementsOnSVG(true);
      })
      .catch((error) => {
        this.isLoadingSearch = false;
        const status = error.status || error.response.status;
        if (status !== 404) {
          this.$emit('loadComplete', false, messages.unknownError);
          this.searchInputClass = 'is-info';
        } else {
          this.searchInputClass = 'is-danger';
        }
        return;
      });
    },
    findElementsOnSVG(zoomOn) {
      if (!this.idsFound) {
        return;
      }
      this.elmFound = [];
      for (let i = 0; i < this.idsFound.length; i += 1) {
        const id = this.idsFound[i].trim();
        const rselector = `#svg-wrapper .rea#${id}`;
        let elms = $(rselector);
        if (elms.length < 1) {
          const selectors = `#svg-wrapper .met.${id}, #svg-wrapper .enz.${id}`;
          elms = $(selectors);
        }
        this.totalSearchMatch = elms.length;
        this.currentSearchMatch = 0;
        for (let j = 0; j < elms.length; j += 1) {
          this.elmFound.push($(elms[j]));
        }
      }
      this.isLoadingSearch = false;
      if (zoomOn) {
        this.centerElementOnSVG(1);
      }
    },
    centerElementOnSVG(increment) {
      if (this.totalSearchMatch === 0) {
        return;
      }
      this.currentSearchMatch += increment;
      if (this.currentSearchMatch < 1) {
        this.currentSearchMatch = this.totalSearchMatch;
      } else if (this.currentSearchMatch > this.totalSearchMatch) {
        this.currentSearchMatch = 1;
      }
      const currentElem = this.elmFound[this.currentSearchMatch - 1];

      this.unSelectElement();
      this.selectElement(currentElem);

      let coords = this.getSvgElemCoordinates(currentElem);
      if (!coords) {
        coords = this.getSvgElemCoordinates($(currentElem).find('.shape')[0]);
      }
      this.panToCoords(coords[4], coords[5]);
    },
    getSvgElemCoordinates(el) {
      // read and parse the transform attribut
      const node = $(el);
      let transform = node.attr('transform');
      if (transform) {
        transform = transform.substring(0, transform.length - 1);
        transform = transform.substring(7, transform.length);
        return transform.split(',').map(parseFloat);
      }
      return null;
    },
    highlightElementsFound() {
      this.highlight(this.elmFound);
    },
    highlight(elements) {
      this.unHighlight();
      this.elmHL = [];
      for (const el of elements) {
        $(el).addClass('hl');
        this.elmHL.push(el);
        if (el.hasClass('rea')) {
          const selectors = `#svg-wrapper .met.${el.attr('id')}`;
          const elms = $(selectors);
          for (const con of elms) {
            $(con).addClass('hl');
            this.elmHL.push(con);
          }
        }
      }
    },
    unHighlight() { // un-highlight elements
      if (this.elmHL) {
        for (let i = 0; i < this.elmHL.length; i += 1) {
          $(this.elmHL[i]).removeClass('hl');
        }
        this.elmHL = [];
      }
    },
    getElementIdAndType(element) {
      if (element.hasClass('rea')) {
        return [element.attr('id'), 'reaction'];
      } else if (element.hasClass('enz')) {
        return [element.attr('class').split(' ')[1], 'enzyme'];
      } else if (element.hasClass('met')) {
        return [element.attr('class').split(' ')[1], 'metabolite'];
      }
      return [element.attr('id'), 'subsystem'];
    },
    selectElement(element) {
      const [id, type] = this.getElementIdAndType(element);
      if (this.selectElementID === id) {
        this.unSelectElement();
        return;
      }

      const selectionData = { type, data: null, error: false };

      this.selectElementID = id;
      if (!element.hasClass('subsystem')) {
        this.highlight([element]);
      }
      if (this.selectedItemHistory[id]) {
        selectionData.data = this.selectedItemHistory[id];
        EventBus.$emit('updatePanelSelectionData', selectionData);
        return;
      }
      if (type === 'subsystem') {
        selectionData.data = { id };
        EventBus.$emit('updatePanelSelectionData', selectionData);
        return;
      }
      EventBus.$emit('startSelectedElement');
      axios.get(`${this.model.database_name}/${type}/${id}`)
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
        selectionData.data = data;
        EventBus.$emit('updatePanelSelectionData', selectionData);
        this.selectedItemHistory[id] = selectionData.data;
        EventBus.$emit('endSelectedElement', true);
      })
      .catch(() => {
        EventBus.$emit('endSelectedElement', false);
      });
    },
    unSelectElement() {
      this.unHighlight();
      this.selectElementID = null;
      EventBus.$emit('unSelectedElement');
    },
    clientFocusX() {
      return ($('.svgbox').width() / 2) + $('#iSideBar').width();
    },
    clientFocusY() {
      return ($('.svgbox').height() / 2) + $('#navbar').height();
    },
    panToCoords(panX, panY) {
      this.$panzoom.panzoom('zoom', 1.0, {
        increment: 1 - this.currentZoomScale,
        transition: false,
        focal: {
          clientX: this.clientFocusX(),
          clientY: this.clientFocusY(),
        },
      });
      this.$panzoom.panzoom('pan', -panX + ($('.svgbox').width() / 2), -panY + ($('.svgbox').height() / 2));
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
    top: 7.25rem;
    left: 2.25rem;
    span:not(:last-child) {
      display: inline-block;
      margin-right: 5px;
    }
  }

  #svgSearch {
    top: 2.25rem;
    left: 30%;
    margin: 0;
    padding: 15px;
    div {
      display: inline-block;
      vertical-align: middle;
    }
    span:first-child {
      color: white;
    }
    #searchInput {
      display: inline-block;
      margin-right: 5px;
      width: 20vw;
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

  #tooltip {
    background: #C4C4C4;
    color: black;
    border-radius: 3px;
    border: 1px solid gray;
    padding: 8px;
    position: absolute;
    display: none;
  }

</style>
