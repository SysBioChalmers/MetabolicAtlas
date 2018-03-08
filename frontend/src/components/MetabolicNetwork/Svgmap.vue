<template>
  <div>
    <div class="svgbox">
      <div id="svg-wrapper" v-html="svgContent">
      </div>
      <div id="svgOption">
        <span class="button" v-on:click="svgfit()">Reset view</span>
        <span class="button" v-on:click="panZoom ? panZoom.zoomIn() : ''">+</span>
        <span class="button" v-on:click="panZoom ? panZoom.zoomOut(): ''">-</span>
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
  components: {
    Loader,
  },
  data() {
    return {
      errorMessage: '',
      loadedComponentType: '',
      loadedComponentName: '',
      loadedCompartment: null,
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
    };
  },
  created() {
    EventBus.$on('showSVGmap', (type, name, ids) => {
      console.log('show svg map');
      console.log(`emit ${type} ${name} ${ids}`);
      if (type === 'compartment') {
        this.HLonly = false;
        this.loadedComponentType = 'compartment';
        this.showCompartment(name);
      } else if (type === 'subsystem') {
        this.HLonly = false;
        this.loadedComponentType = 'subsystem';
        this.showTiles(name, ids);
      } else if (type === 'tiles') {
        this.HLonly = false;
        this.loadedComponentType = 'tiles';
        this.showTiles(name, ids);
      } else if (type === 'highlight') {
        this.HLonly = true;
        this.loadedComponentType = 'highlight';
        this.hlElements(null, ids);
      } else if (type === 'find') {
        this.HLonly = false;
        this.loadedComponentType = 'find';
        this.hlElements(name, ids);
      } else if (!this.svgName || type === 'wholemap') {
        this.loadedComponentType = 'wholemap';
        const compartment = getCompartmentFromName('wholemap');
        this.loadSVG(compartment, null);
      }
    });
  },
  mounted() {
    // $('#svgbox').attr('width', '100%');
    // $('#svgbox').attr('height', `${$(window).height() - 300}`);

    // add a white reactange behind the name
    /*  $('#svg-wrapper').on('mouseover', '.metabolite, .reaction', function f() {
      const text = $(this)[0].children[1];
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      const SVGRect = $(this)[0].children[1].getBBox();
      rect.setAttribute('x', SVGRect.x - 2);
      rect.setAttribute('y', SVGRect.y - 1);
      rect.setAttribute('width', SVGRect.width + 4);
      rect.setAttribute('height', SVGRect.height + 2);
      rect.setAttribute('fill', 'white');
      $(this)[0].insertBefore(rect, text);
    });
    // remove the white rectangle
    $('#svg-wrapper').on('mouseout', '.metabolite, .reaction', function f() {
      $(this)[0].removeChild($(this)[0].children[3]);
    }); */
    //  enzymes are also .metabolite
    $('#svg-wrapper').on('click', '.metabolite', function f() {
      // exact the real id from the id
      const id = $(this).attr('id').split('-')[0].trim();
      // console.log(id);
      if (id[0] === 'E') {
        EventBus.$emit('updateSelTab', 'enzyme', id);
      } else {
        EventBus.$emit('updateSelTab', 'metabolite', id);
      }
    });
    $('#svg-wrapper').on('click', '.reaction', function f() {
      // exact the real id from the id
      const id = $(this).attr('id');
      EventBus.$emit('updateSelTab', 'reaction', id);
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
            // console.log(oldzl);
            // console.log(newzl);
            if (newzl > this.loadedCompartment.maxZoomLvl + 0.001) {
              this.allowZoom = false;
              return false;
            } else if (newzl < this.loadedCompartment.minZoomLvl - 0.001) {
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
            if (zc >= this.loadedCompartment.RenderZoomLvl.metaboliteLabel) {
              $('.metabolite .lbl, .reaction .lbl').attr('display', 'inline');
            } else {
              $('.metabolite .lbl, .reaction .lbl').attr('display', 'none');
            }
            if (zc >= this.loadedCompartment.RenderZoomLvl['flux-edge']) {
              $('.flux-edge, .effector-edge').attr('display', 'inline');
            } else {
              $('.flux-edge, .effector-edge').attr('display', 'none');
            }
            if (zc >= this.loadedCompartment.RenderZoomLvl.metabolite) {
              $('.metabolite, .reaction').attr('display', 'inline');
            } else {
              $('.metabolite, .reaction').attr('display', 'none');
            }
          },
        });
        this.svgfit();
        this.unHighlight();
        if (callback) {
          // call findElementsOnSVG
          callback();
        } else {
          this.$emit('loadedComponent', true, this.loadedComponentType,
            this.loadedComponentName, '');
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
        // this.showLoader = false;
      }
    },
    loadSVG(compartment, callback) {
      // console.log('load svg');
      // load the svg file from the server
      // if aleady loaded, just call the callback funtion
      const newSvgName = compartment.svgName;
      const svgLink = `${window.location.origin}/svgs/${newSvgName}.svg`;
      this.$emit('loading');
      if (!newSvgName) {
        // TODO remove this when all svg files are available
        this.$emit('loadedComponent', false, this.loadedComponentType,
         this.loadedComponentName, 'Svg file \'newSvgName\' not available');
        return;
      }

      if (newSvgName !== this.svgName) {
        // console.log('new svg');
        axios.get(svgLink)
          .then((response) => {
            // console.log('get the svg');
            this.svgContent = response.data;
            this.svgName = newSvgName;
            this.loadedCompartment = compartment;
            setTimeout(() => {
              // this.showLoader = false;
              this.loadSvgPanZoom(callback);
            }, 0);
          })
          .catch((error) => {
            // TODO: handle error
            console.log(error);
            this.$emit('loadedComponent', false, this.loadedComponentType,
              this.loadedComponentName, error);
          });
      } else if (callback) {
        this.loadedCompartment = compartment;
        // call findElementsOnSVG
        callback();
      } else {
        this.loadedCompartment = compartment;
        // console.log('finish call svgfit');
        this.svgfit();
        this.$emit('loadedComponent', true, this.loadedComponentType,
         this.loadedComponentName, '');
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
        this.$emit('loadedComponent', true, this.loadedComponentType,
         this.loadedComponentName, '');
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
        this.$emit('loadedComponent', true, this.loadedComponentType,
         this.loadedComponentName, '');
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
      if (newScale > this.loadedCompartment.maxZoomLvl) {
        // fix zoom round e.g. 30 => 30.00001235
        newScale = this.loadedCompartment.maxZoomLvl - 0.01;
      }
      console.log('zoom at');
      console.log(newScale);
      this.panZoom.zoom(newScale);
      this.$emit('loadedComponent', true, this.loadedComponentType,
         this.loadedComponentName, '');
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
    hlElements(compartmentName, ids) {
      if (compartmentName) {
        const compartment = getCompartmentFromName(compartmentName);
        this.ids = ids;
        if (compartment) {
          this.loadSVG(compartment, this.findElementsOnSVG);
        }
      } else {
        this.unHighlight();
        this.ids = ids;
        if (ids) {
          this.findElementsOnSVG();
        }
      }
    },
    showTiles(compartmentName, coordinate) {
      if (compartmentName) {
        const compartment = getCompartmentFromName(compartmentName);
        if (compartment) {
          this.updateZoomBoxCoor(coordinate);
          this.loadSVG(compartment, this.zoomOnTiles);
        }
      }
    },
    showCompartment(compartmentName) {
      if (compartmentName) {
        const compartment = getCompartmentFromName(compartmentName);
        if (compartment) {
          this.loadSVG(compartment, null);
        }
      }
    },
    getCompartmentFromName,
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

  .metabolite, .reaction {
    .shape, .lbl {
      cursor: pointer;
    }

    &:hover {
      .shape {
        fill: red;
      }
      .lbl {
        font-weight: 900;
        text-shadow: 0 0 3px gray;
      }
    }
  }

  .svgbox {
    position: relative;
    margin: 0;
    width: 100%;
    height:100%;
  }

  #svgOption {
    position: absolute;
    top: 10px;
    left: 10px;
    height: 30px;
    z-index: 10;

    span {
      display: inline-block;
      margin-right: 5px;
    }
  }

  svg .hl {
    fill: #22FFFF;
  }

  svg .hl2 {
    fill: red;
  }

</style>
