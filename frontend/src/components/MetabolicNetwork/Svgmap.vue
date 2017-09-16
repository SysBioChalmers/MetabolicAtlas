<template>
  <div>
    <loader v-show="showLoader"></loader>
    <div v-show="!showLoader">
      <div v-show="!showMissingSVGString" class="svgbox">
        <div id="svg-wrapper" v-html="svgContent">
        </div>
        <div id="svgOption">
          <span class="button" v-show="!showMissingSVGString" v-on:click="svgfit()">Reset view</span>
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
import { getCompartmentFromCID, getCompartmentFromName } from '../../helpers/compartment';
import { default as EventBus } from '../../event-bus';

export default {
  name: 'svgmap',
  components: {
    Loader,
  },
  data() {
    return {
      errorMessage: '',
      compartment: null,
      showResults: false,
      showMissingSVGString: true,
      showLoader: false,
      svgContent: null,
      svgName: '',
      svgBigMapName: 'whole_metabolic_network_without_details',
      panZoom: null,
      ids: [],
      HLelms: [],
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
    };
  },
  created() {
    EventBus.$on('showSVGmap', (type, id, ids) => {
      // console.log('show svg map');
      // console.log(`emit ${type} ${id} ${ids}`);
      if (type === 'compartment') {
        this.hlElements(id, ids);
      } else if (type === 'subsystem') {
        console.log('run subsystem');
      } else if (type === 'tiles') {
        console.log('run tiles');
        this.showTiles(id, ids);
      } else if (type === 'wholemap') {
        this.loadSVG(this.svgBigMapName, this.swapSVG, null);
      }
    });
    // this.loadSVG(this.svgBigMapName, this.swapSVG, null);
  },
  mounted() {
    // console.log('svgmap mounted');
    $('#svgbox').attr('width', '100%');
    $('#svgbox').attr('height', `${$(window).height() - 300}`);
    $('#svg-wrapper').on('mouseover', '.Metabolite, .Reaction', function f() {
      const text = $(this)[0].children[1].children[0];
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      const SVGRect = $(this)[0].children[1].getBBox();
      rect.setAttribute('x', SVGRect.x - 2);
      rect.setAttribute('y', SVGRect.y - 1);
      rect.setAttribute('width', SVGRect.width + 4);
      rect.setAttribute('height', SVGRect.height + 2);
      rect.setAttribute('fill', 'white');
      $(this)[0].children[1].insertBefore(rect, text);
    });
    $('#svg-wrapper').on('mouseout', '.Metabolite, .Reaction', function f() {
      $(this)[0].children[1].removeChild($(this)[0].children[1].children[0]);
    });
    $('#svg-wrapper').on('click', '.Metabolite', function f() {
      const id = $(this).attr('id').substring(11).split('$')[0].trim();
      if (id[0] === 'E') {
        EventBus.$emit('updateSelTab', 'enzyme', id);
      } else {
        EventBus.$emit('updateSelTab', 'metabolite', id);
      }
    });
    $('#svg-wrapper').on('click', '.Reaction', function f() {
      const id = $(this).attr('id').substring(9).split('$')[0];
      EventBus.$emit('updateSelTab', 'reaction', id);
    });
  },
  methods: {
    swapSVG(callback) {
      // console.log('swap svg');
      setTimeout(() => {
        this.panZoom = svgPanZoom('#svg-wrapper svg', {
          zoomEnabled: true,
          controlIconsEnabled: false,
          minZoom: 0.5,
          maxZoom: 15,
          zoomScaleSensitivity: 0.5,
          fit: true,
          onZoom() {
            console.log(`rz: ${this.getSizes().realZoom} | zoom ${this.getZoom()}`);
          },
        });
        this.svgfit();
        this.unHighlight();
        if (callback) {
          // call getElements
          callback();
        }
      }, 0);
    },
    svgfit() {
      // console.log('fit svg');
      $('#svg-wrapper svg').attr('width', '100%');
      const h = $('.svgbox').first().css('height');
      $('#svg-wrapper svg').attr('height', h);
      this.panZoom.resize(); // update SVG cached size and controls positions
      this.panZoom.fit();
      this.panZoom.center();
      this.showLoader = false;
    },
    loadSVG(svgName, callback, callback2) {
      // console.log('run load svg');
      const newSvgName = svgName;
      const svgLink = `${window.location.origin}/svgs/${newSvgName}.svg`;
      this.showLoader = true;
      if (!newSvgName) {
        // TODO remove this when all svg files available
        this.showMissingSVGString = true;
        this.showLoader = false;
        return;
      }
      this.showMissingSVGString = false;
      // console.log(`newSvgName ${newSvgName}`);
      if (newSvgName !== this.svgName) {
        // console.log('new svg');
        axios.get(svgLink)
          .then((response) => {
            // console.log('get the svg');
            this.svgContent = response.data;
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
        // console.log('not new svg');
        this.unHighlight();
        if (callback2) {
          // call getElements
          callback2();
        } else {
          this.svgfit();
        }
      }
    },
    getElement() {
      // console.log('call getelements');
      // console.log(this.ids);
      const a = [];
      const debug = false;
      if (!this.ids) {
        this.showLoader = false;
        return;
      }
      if (debug) {
        // this.ids = ['E_2778', 'M_m03106s', 'M_m02041p', 'fake1', 'fake3', 'fake5'];
        // this.ids = ['fake5', 'fake4'];
        this.ids = ['fake1', 'fake4'];
      }
      for (const type of ['Metabolite', 'Enzyme', 'Reaction']) {
        for (let i = 0; i < this.ids.length; i += 1) {
          const id = this.ids[i].trim();
          let idname = `#${type}\\$${id}`;
          let elm = $(idname);
          if (elm.length) {
            // console.log(idname);
            a.push(elm);
          } else {
            // console.log(`${idname} elem not found`);
          }
          for (let j = 1; j < 100; j += 1) {
            idname = `#${type}\\$${id}\\$${j}`;
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
      }
      if (a.length) {
        this.highlightSVGelements(a);
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
      // console.log(this.zoomBox);
    },
    getTransform(el) {
      let transform = el.attr('transform');
      transform = transform.substring(0, transform.length - 1);
      transform = transform.substring(7, transform.length);
      return transform.split(',').map(parseFloat);
    },
    highlightSVGelements(els) {
      // console.log('call hl');
      // console.log('els');
      // console.log(els);
      const debug = false;
      this.resetZoombox();
      for (const el of els) {
        const id = el.attr('id').replace(/[$]/g, '\\$');
        const path = $(`#${id} path`);
        if (debug) {
          console.log(id);
          console.log(el[0].getBBox());
          console.log(path);
          console.log(path[0].getBBox());
        }
        path.addClass('hl');
        this.HLelms.push(path);
        // const transform = this.getTransform(path);
        // const zptransform = this.getTransform($('.svg-pan-zoom_viewport'));

        // const rx = el[0].getBBox().x + (el[0].getBBox().width / 2);
        // const ry = el[0].getBBox().y + (el[0].getBBox().height / 2);
        // const rx = parseInt(transform[4], 10);
        // const ry = parseInt(transform[5], 10);
        this.updateZoomBox(el[0]); // dom element
      }
      this.zoomOnTiles();
    },
    zoomOnTiles() {
      // console.log('zoom tiles');
      this.getCenterZoombox();
      const realZoom = this.panZoom.getSizes().realZoom;
      this.panZoom.pan({
        x: -(this.zoomBox.centerX * realZoom) + (this.panZoom.getSizes().width / 2),
        y: -(this.zoomBox.centerY * realZoom) + (this.panZoom.getSizes().height / 2),
      });
      const viewBox = this.panZoom.getSizes().viewBox;
      const debug = false;
      if (debug) {
        console.log(this.zoomBox.w);
        console.log(viewBox.width);
        console.log(this.zoomBox.h);
        console.log(viewBox.height);
      }
      let newScale = Math.min(viewBox.width / this.zoomBox.w, viewBox.height / this.zoomBox.h);
      if (newScale > this.compartment.maxZoomLvl) {
        newScale = this.compartment.maxZoomLvl;
      }
      this.panZoom.zoom(newScale);
      this.showLoader = false;
    },
    unHighlight() {
      if (this.HLelms) {
        // un-highligh elements
        for (let i = 0; i < this.HLelms.length; i += 1) {
          this.HLelms[i].removeClass('hl');
        }
        this.HLelms = [];
      }
    },
    hlElements(compartmentID, ids) {
      if (compartmentID) {
        this.compartment = getCompartmentFromCID(compartmentID);
        this.ids = ids;
        this.loadSVG(this.compartment.svgName, this.swapSVG, this.getElement);
      }
    },
    showTiles(compartmentL, coordinate) {
      // console.log('showTiles');
      if (compartmentL) {
        console.log(compartmentL);
        this.compartment = getCompartmentFromName(compartmentL);
        this.updateZoomBoxCoor(coordinate);
        console.log(this.zoomBox);
        this.loadSVG(this.compartment.svgName, this.swapSVG, this.zoomOnTiles);
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

  .Metabolite, .Reaction {
    .Shape, .Label {
      cursor: pointer;
    }

    &:hover {
      .Shape {
        path {
          fill: red;
        }
      }
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
