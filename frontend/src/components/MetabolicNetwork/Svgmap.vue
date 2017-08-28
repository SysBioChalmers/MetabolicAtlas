<template>
  <div>
    <loader v-show="showLoader"></loader>
    <div v-show="!showLoader">
      <div v-show="!showMissingSVGString" class="svgbox">
        <div id="svg-wrapper" v-html="svgContent">
        </div>
        <div id="svgOption">
          <span class="button" v-show="!showMissingSVGString" v-on:click="svgfit()">RESET</span>
        </div>
      </div>
      <div class="svgbox has-text-centered" v-show="showMissingSVGString">
        Sorry, the SVG file is not available for this compartment
      </div>
    </div>
  </div>
</template>

<script>

import $ from 'jquery';
import axios from 'axios';
import svgPanZoom from 'svg-pan-zoom';
import Loader from 'components/Loader';
import { getCompartmentFromCID } from '../../helpers/compartment';
import { default as EventBus } from '../../event-bus';

export default {
  name: 'svgmap',
  components: {
    Loader,
  },
  data() {
    return {
      errorMessage: '',
      showResults: false,
      showMissingSVGString: true,
      showLoader: false,
      svgContent: null,
      svgName: '',
      panZoom: null,
      ids: [],
      HLelms: [],
      zoomBox: {
        minX: 99999,
        maxX: 0,
        minY: 99999,
        maxY: 0,
      },
    };
  },
  created() {
    EventBus.$on('showSVGmap', (compartmentID, ids) => {
      console.log(`emit ${compartmentID} ${ids}`);
      this.hlElements(compartmentID, ids);
    });
  },
  mounted() {
    console.log('svgmap mounted');
    // this.loadSVG(1, this.swapSVG);
    $('#svgbox').attr('width', '100%');
    $('#svgbox').attr('height', `${$(window).height() - 300}`);
  },
  methods: {
    swapSVG(callback) {
      console.log('swap svg');
      setTimeout(() => {
        this.panZoom = svgPanZoom('#svg-wrapper svg', {
          zoomEnabled: true,
          controlIconsEnabled: false,
          minZoom: 0.0001,
          maxZoom: 100,
          zoomScaleSensitivity: 0.6,
          fit: true,
          onZoom() {
            console.log(`rz: ${this.getSizes().realZoom} | zoom ${this.getZoom()}`);
          },
        });
        this.svgfit();
        this.unHighlight();
        if (callback && this.ids) {
          // call getElements
          callback();
        }
      }, 0);
    },
    svgfit() {
      console.log('fit svg');
      $('#svg-wrapper svg').attr('width', '100%');
      const h = $('.svgbox').first().css('height');
      $('#svg-wrapper svg').attr('height', h);
      this.panZoom.resize(); // update SVG cached size and controls positions
      this.panZoom.fit();
      this.panZoom.center();
    },
    loadSVG(svgName, callback, callback2) {
      const newSvgName = svgName;
      const svgLink = `${window.location.origin}/svgs/${newSvgName}.svg`;
      if (!newSvgName) {
        // TODO remove this when all svg files available
        this.showMissingSVGString = true;
        this.showLoader = false;
        return;
      }
      this.showMissingSVGString = false;
      if (newSvgName !== this.svgName) {
        console.log('new svg');
        axios.get(svgLink)
          .then((response) => {
            console.log('get the svg');
            this.svgContent = response.data;
            this.showLoader = true;
            this.svgName = newSvgName;
            setTimeout(() => {
              this.showLoader = false;
              if (callback) {
                callback(callback2);
              }
            }, 0);
          })
          .catch((error) => {
            // TODO: handle error
            console.log(error);
            this.showLoader = false;
            this.showMissingSVGString = true;
          });
      } else {
        console.log('not new svg');
        this.unHighlight();
        console.log(this.ids.length);
        if (callback2 && this.ids.length) {
          // call getElements
          callback2();
        } else {
          this.svgfit();
        }
        this.showLoader = false;
      }
    },
    getElement() {
      console.log('call getelements');
      console.log(this.ids);
      const a = [];
      const debug = false;
      // const ids2 = ['E_2778', 'M_m03106s', 'M_m02041p'];
      for (const type of ['Metabolite', 'Enzyme']) {
        for (let i = 0; i < this.ids.length; i += 1) {
          const id = this.ids[i].trim();
          let idname = `#${type}\\$${id}`;
          console.log(idname);
          let elm = $(idname);
          console.log(idname);
          if (elm.length) {
            console.log(elm);
            idname = `#${type}\\$${id} path`;
            elm = $(idname);
            if (debug) {
              console.log(elm[0].getBBox());
            }
            a.push(elm);
          } else {
            console.log(`${idname} elem not found`);
          }
          for (let j = 1; j < 30; j += 1) {
            idname = `#${type}\\$${id}\\$${j}`;
            elm = $(idname);
            if (debug) {
              console.log(`${type}$${id}$${j}`);
            }
            if (elm.length) {
              idname = `#${type}\\$${id}\\$${j} path`;
              elm = $(idname);
              if (debug) {
                console.log(elm[0].getBBox());
                elm.click(function f() {
                  console.log(this);
                });
              }
              console.log(elm);
              a.push(elm);
            } else {
              console.log(`${idname} elem not found`);
              break;
            }
          }
        }
      }
      this.highlightSVGelements(a);
    },
    getTransform(el) {
      let transform = el.attr('transform');
      transform = transform.substring(0, transform.length - 1);
      transform = transform.substring(7, transform.length);
      return transform.split(',').map(parseFloat);
    },
    highlightSVGelements(els) {
      console.log('call hl');
      for (const el of els) {
        console.log(el);
        el.addClass('hl');
        const transform = this.getTransform(el);
        // const zptransform = this.getTransform($('.svg-pan-zoom_viewport'));

        const rx = parseInt(transform[4], 10);
        const ry = parseInt(transform[5], 10);
        const realZoom = this.panZoom.getSizes().realZoom;
        this.panZoom.pan({
          x: -(rx * realZoom) + (this.panZoom.getSizes().width / 2),
          y: -(ry * realZoom) + (this.panZoom.getSizes().height / 2),
        });
        this.panZoom.zoom(5);
      }
      this.HLelms = els;
    },
    unHighlight() {
      if (this.HLelms) {
        // un-highligh elements
        for (let i = 0; i < this.HLelms.length; i += 1) {
          this.HLelms[i].removeClass('hl');
        }
      }
    },
    hlElements(compartmentID, ids) {
      if (compartmentID) {
        const svgName = getCompartmentFromCID(compartmentID).svgName;
        this.ids = ids;
        this.loadSVG(svgName, this.swapSVG, this.getElement);
        // const a = this.getElement(ids);
      }
    },
    getCompartmentFromCID,
  },
};
</script>

<style lang="scss">

  #svg-wrapper {
    margin: auto;
    width: 100%;
    img {
      padding: 20px;
      width: 600px;
      margin: auto;
    }
  }

  .svgbox {
    position: relative;
    margin: auto;
    width:1200px;
    height:700px;
    border: 1px solid black;
  }

  #svgOption {
    position: absolute;
    top: 10px;
    left: 10px;
    width: 50px;
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

</style>
