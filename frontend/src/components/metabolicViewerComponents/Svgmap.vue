<template>
  <div>
    <div class="svgbox">
      <div id="svg-wrapper" v-html="svgContent">
      </div>
      <div id="svgOption" class="overlay">
        <span class="button" v-on:click="panZoom ? panZoom.zoomIn() : ''"><i class="fa fa-search-plus"></i></span>
        <span class="button" v-on:click="panZoom ? panZoom.zoomOut(): ''"><i class="fa fa-search-minus"></i></span>
        <span class="button" v-on:click="svgfit()"><i class="fa fa-arrows-alt"></i></span>
      </div>
      <div id="svgSearch" class="overlay">
        <span>Search:</span><input class="input" />
      </div>
    </div>
  </div>
</template>

<script>

import $ from 'jquery';
import axios from 'axios';
import svgPanZoom from 'svg-pan-zoom';
import Loader from 'components/Loader';
import { getCompartmentFromName } from '../../helpers/compartment';
import { default as EventBus } from '../../event-bus';

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
      svgContent: null,
      svgName: '',
      svgBigMapName: 'whole_metabolic_network_without_details',
      panZoom: null,
      ids: [],
      HLelms: [],
      HLonly: false,
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
      allowZoom: true,
      dragging: false,
    };
  },
  created() {
    EventBus.$on('showSVGmap', (type, name, ids, forceReload) => {
      console.log('show svg map');
      console.log(`emit ${type} ${name} ${ids} ${forceReload}`);
      if (forceReload) {
        this.svgName = '';
      }
      if (type === 'compartment') {
        this.HLonly = false;
        this.showMap(name);
      } else if (type === 'subsystem') {
        this.HLonly = false;
        this.showTiles(name, ids);
      } else if (type === 'tiles') {
        this.HLonly = false;
        this.showTiles(name, ids);
      } else if (type === 'highlight') {
        this.HLonly = true;
        this.hlElements(null, ids);
      } else if (type === 'find') {
        this.HLonly = false;
        this.hlElements(name, ids);
      } else if (!this.svgName || type === 'wholemap') {
        // const compartment = getCompartmentFromName('wholemap');
        this.loadSVG('wholemap', null);
      }
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
        // const ZL = this.zoomLevel;
        this.panZoom = svgPanZoom('#svg-wrapper svg', {
          zoomEnabled: true,
          controlIconsEnabled: false,
          minZoom: 0.5,
          maxZoom: 30,
          zoomScaleSensitivity: 0.4,
          fit: true,
          beforeZoom: (oldzl, newzl) => {
            if (newzl > this.loadedMap.maxZoomLvl + 0.001) {
              this.allowZoom = false;
              return false;
            } else if (newzl < this.loadedMap.minZoomLvl - 0.001) {
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
          onZoom: (zc) => {
            // console.log(`rz: ${this.getSizes().realZoom} | zoom ${this.getZoom()}`);
            this.zoomLevel = zc;
            if (zc >= this.loadedMap.RenderZoomLvl.metaboliteLabel) {
              $('.met .lbl, .rea .lbl, .enz .lbl').attr('display', 'inline');
            } else {
              $('.met .lbl, .rea .lbl, .enz .lbl').attr('display', 'none');
            }
            if (zc >= this.loadedMap.RenderZoomLvl.metabolite) {
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
          this.$emit('loadedComponent', true, '');
        }
      }, 0);
    },
    svgfit() {
      // console.log('fit svg');
      $('#svg-wrapper svg').attr('width', '100%');
      // const h = $('.svgbox').first().css('height');
      const a = $('.svgbox').first().offset().top;
      const vph = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
      // console.log(`h: ${h}`);
      // console.log(`a: ${a}`);
      // console.log(`vph: ${vph}`);
      const v = vph - a;

      $('#svg-wrapper svg').attr('height', `${v}px`);
      if (this.panZoom) {
        this.panZoom.resize(); // update SVG cached size
        this.panZoom.fit();
        this.panZoom.center();
      }
    },
    loadSVG(id, callback) {
      // console.log('load svg');
      // load the svg file from the server
      // if aleady loaded, just call the callback funtion
      const currentLoad = getCompartmentFromName(id);
      if (!currentLoad) {
        this.$emit('loadedComponent', false, '');
        return;
      }
      const newSvgName = currentLoad.svgName;
      const svgLink = `${window.location.origin}/svgs/${newSvgName}.svg`;
      this.$emit('loading');
      if (!newSvgName) {
        // TODO remove this when all svg files are available
        this.$emit('loadedComponent', false, 'SVG map not available.');
        return;
      }

      if (newSvgName !== this.svgName) {
        // console.log('new svg');
        axios.get(svgLink)
          .then((response) => {
            // console.log('get the svg');
            this.svgContent = response.data;
            this.svgName = newSvgName;
            this.loadedMap = currentLoad;
            setTimeout(() => {
              // this.showLoader = false;
              this.loadSvgPanZoom(callback);
            }, 0);
          })
          .catch((error) => {
            // TODO: handle error
            console.log(error);
            this.$emit('loadedComponent', false, error);
          });
      } else if (callback) {
        this.loadedMap = currentLoad;
        // call findElementsOnSVG
        callback();
      } else {
        this.loadedMap = currentLoad;
        // console.log('finish call svgfit');
        this.svgfit();
        this.$emit('loadedComponent', true, '');
      }
    },
    findElementsOnSVG() {
      console.log('call findElementsOnSVGs');
      const a = [];
      if (!this.ids) {
        this.showLoader = false;
        return;
      }
      for (let i = 0; i < this.ids.length; i += 1) {
        const id = this.ids[i].trim();
        let idname = `#${id}`;
        let elm = $(idname);
        if (elm.length) {
          a.push(elm);
        }
        for (let j = 0; j < 200; j += 1) {
          idname = `#${id}-${j}`;
          elm = $(idname);
          if (elm.length) {
            // console.log(idname);
            a.push(elm);
          } else {
            // console.log(`${idname} elem not found`);
            break;
          }
        }
      }
      if (a.length) {
        this.highlightSVGelements(a);
      } else {
        // this.showLoader = false;
        this.$emit('loadedComponent', true, '');
      }
    },
    updateZoomBoxCoor(coordinate) {
      this.zoomBox.minX = coordinate.minX;
      this.zoomBox.maxX = coordinate.maxX;
      this.zoomBox.minY = coordinate.minY;
      this.zoomBox.maxY = coordinate.maxY;
    },
    updateZoomBox(el) {
      const x = el.getBBox().x;
      const y = el.getBBox().y;
      const w = el.getBBox().width;
      const h = el.getBBox().height;
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
      // read and parse the transform attribut, no used anymore
      let transform = el.attr('transform');
      transform = transform.substring(0, transform.length - 1);
      transform = transform.substring(7, transform.length);
      return transform.split(',').map(parseFloat);
    },
    highlightSVGelements(els) {
      this.unHighlight();
      this.resetZoombox();
      for (const el of els) {
        const id = el.attr('id');
        const path = $(`#${id} path`);
        // change the box color only
        this.HLelms.push(path);
        if (!this.HLonly) {
          path.addClass('hl');
          this.updateZoomBox(el[0]); // the DOM element
        } else {
          path.addClass('hl2');
          el.attr('display', 'inline');
        }
      }
      if (!this.HLonly) {
        this.zoomOnTiles();
      } else {
        this.$emit('loadedComponent', true, '');
      }
    },
    zoomOnTiles() {
      console.log('zoom tiles');
      this.getCenterZoombox();
      const realZoom = this.panZoom.getSizes().realZoom;
      this.panZoom.pan({
        x: -(this.zoomBox.centerX * realZoom) + (this.panZoom.getSizes().width / 2),
        y: -(this.zoomBox.centerY * realZoom) + (this.panZoom.getSizes().height / 2),
      });
      const viewBox = this.panZoom.getSizes().viewBox;
      let newScale = Math.min(viewBox.width / this.zoomBox.w, viewBox.height / this.zoomBox.h);
      // console.log(`newScale ${newScale}`);
      if (newScale > this.loadedMap.maxZoomLvl) {
        // fix zoom round e.g. 30 => 30.00001235
        newScale = this.loadedMap.maxZoomLvl - 0.01;
      }
      console.log('zoom at');
      console.log(newScale);
      this.panZoom.zoom(newScale);
      this.$emit('loadedComponent', true, '');
    },
    unHighlight() {
      if (this.HLelms) {
        // un-highlight elements
        for (let i = 0; i < this.HLelms.length; i += 1) {
          this.HLelms[i].removeClass('hl');
          this.HLelms[i].removeClass('hl2');
        }
        this.HLelms = [];
      }
    },
    hlElements(id, ids) {
      this.ids = ids;
      if (id) {
        // const compartment = getCompartmentFromName(compartmentName);
        this.loadSVG(id, this.findElementsOnSVG);
      } else {
        this.unHighlight();
        if (ids) {
          this.findElementsOnSVG();
        }
      }
    },
    showTiles(id, coordinate) {
      if (id) {
        // const compartment = getCompartmentFromName(compartmentName);
        this.updateZoomBoxCoor(coordinate);
        this.loadSVG(id, this.zoomOnTiles);
      }
    },
    showMap(id) {
      if (id) {
        // const compartment = getCompartmentFromName(compartmentName);
        this.loadSVG(id, null);
      }
    },
    selectElement(id, type) {
      EventBus.$emit('startSelectedElement');
      axios.get(`${this.model}/${type}s/${id}`)
      .then((response) => {
        let data = response.data;
        if (type === 'reaction') {
          data = data.reaction;
        }
        data.type = type;
        EventBus.$emit('updatePanelSelectionData', data);
        EventBus.$emit('endSelectedElement', true);
      })
      .catch((error) => {
        console.log(error);
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
  #svg-wrapper {
    margin: 0;
    svg {
      width: 100%;
    }
  }

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
    width: 100%;
    height:100%;
  }

  .overlay {
    position: absolute;
    z-index: 10;
    padding: 15px;
    border: 2px solid black;
    border-radius: 5px;
    background: rgba(13, 13, 13, 0.8);
  }

  #svgOption {
    position: absolute;
    top: 2rem;
    left: 2rem;
    span {
      display: inline-block;
      margin-right: 5px;
    }
  }

  #svgSearch {
    top: 2rem;
    left: 25%;
    width: 50%;
    span {
      display: inline-block;
      margin: 5px 10px 5px 0px;
      color: white;
    }
    input {
      display: inline-block;
      width: 80%;
    }
  }

  svg .hl {
    fill: #22FFFF;
  }

  svg .hl2 {
    fill: red;
  }

</style>
