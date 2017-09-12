<template>
  <div id="reporter-metabolites">
    <div class="columns">
      <div class="column is-2">
        <div class="field">
          <div class="">
            <label class="label">IDs: </label>
          </div>
          <p class="control">
            <textarea id="idarea" class="textarea" ref="textarea" placeholder="udp, h2o2, sam, m_m01784n">udp, h2o2, sam, m_m01784n</textarea>
          </p>
        </div>
        <div>
          <button class="button is-primary" @click="searchElements">Search</button>
        </div>
        <div id="table-res" v-show="showResults">
          <span class="help is-small">Click on a row to highlight the corresponding components</span>
          <table class="table">
            <thead>
              <tr>
                <th>Compartment</th>
                 <th>Elements<br>found</th>
              </tr>
            </thead>
            <tbody>
              <tr class="m-tr" v-for="v, k in results"
                @click="hlElements($event, k, v)">
                <td>{{ getCompartmentFromCID(k).name }}</td>
                <td>{{ v.length  }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="column is-10">
        <button id="swap" style="padding: 5px 20px; background: red; border: 1px solid #ff0404;"
        @click="swapSVG">swap</button>
        <loader v-show="showLoader"></loader>
        <div v-show="!showLoader" id="svgbox">
          <div id="svg-wrapper2" v-html="svgContent">
          </div>
          <div id="svgOption">
            <span class="button" v-show="!showMissingSVGString" v-on:click="panZoom.reset()">RESET</span>
            <span class="button" v-show="!showMissingSVGString" v-on:click="svgfit">FIT</span>
          </div>
          <div id="svgMissing" v-show="showMissingSVGString">
            The SVG file is not yet available for this compartment
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

// import { default as snap } from 'snapsvg';
import $ from 'jquery';
import axios from 'axios';
import svgPanZoom from 'svg-pan-zoom';
import Loader from 'components/Loader';
import { getCompartmentFromCID } from '../helpers/compartment';

/* eslint-disable global-require, no-dynamic-require */
export default {
  name: 'reporter-metabolites',
  components: {
    Loader,
  },
  data() {
    return {
      errorMessage: '',
      showResults: false,
      showMissingSVGString: true,
      showLoader: true,
      svgContent: null,
      svgName: '',
      compartmentID: 0,
      results: {},
      HLelms: [],
      switched: true,
      panZoom: null,
      ids: [],
      zoomBox: {
        minX: 99999,
        maxX: 0,
        minY: 99999,
        maxY: 0,
      },
      lastEmbed: null,
      lastEmbedSrc: null,
      lastEventListener: null,
    };
  },
  mounted() {
    this.loadSVG(1, this.swapSVG);
    $('#svgbox').attr('width', '100%');
    $('#svgbox').attr('height', `${$(window).height() - 300}`);
  },
  methods: {
    swapSVG(callback) {
      console.log('call swapSVG');
      setTimeout(() => {
        console.log('svgPanZoom start');
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
        if (callback) {
          console.log('call back swapsvg');
          callback();
        }
      }, 0);
    },
    svgfit() {
      console.log('call svg fit');
      $('#svg-wrapper svg').attr('width', '100%');
      $('#svg-wrapper svg').attr('height', `${$('#svgbox').attr('height')}`);
      this.panZoom.resize(); // update SVG cached size and controls positions
      this.panZoom.fit();
      this.panZoom.center();
      console.log(this.panZoom);
      console.log('end svg fit');
    },
    loadSVG(compartmentID, callback, callback2) {
      console.log('call loadsvg');
      const newSvgName = getCompartmentFromCID(compartmentID).svgName;
      const svgLink = `${window.location.origin}/svgs/${newSvgName}.svg`;
      if (!newSvgName) {
        // TODO remove this when all svg files available
        this.showMissingSVGString = true;
        // this.svgContent = '';
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
          });
      } else {
        console.log('not new svg');
        if (callback2) {
          callback2();
        }
        this.showLoader = false;
      }
      console.log('en load svg');
    },
    getElement() {
      console.log('call getelements');
      console.log(this.panZoom.getSizes());
      const debug = true;
      console.log(this.ids);
      const a = [];
      const ids2 = ['E_2778', 'M_m03106s', 'M_m02041p'];
      for (const type of ['Metabolite', 'Enzyme']) {
        for (let i = 0; i < ids2.length; i += 1) {
          const id = ids2[i].trim();
          let elm = $(`#${type}_${id}`);
          console.log(`#${type}_${id}`);
          if (elm.length) {
            console.log(elm);
            // console.log(elm[0].getBBox());
            elm = $(`#${type}_${id} path`);
            if (debug) {
              console.log(elm[0].getBBox());
            }
            // this.updateZoomBox(elm.getBBox());
            a.push(elm);
          } else {
            console.log(`${id} elem not found`);
            // break;
          }
          for (let j = 2; j < 3; j += 1) {
            elm = $(`#${type}_${id}_${j}`);
            if (debug) {
              console.log(`${type}_${id}_${j}`);
            }
            if (elm.length) {
              elm = $(`#${type}_${id}_${j} path`);
              if (debug) {
                // console.log(`${type}_${id}_${j} box : ${elm.getBBox()}`);
                elm.click(function f() {
                  console.log(this);
                });
              }
              // this.updateZoomBox(elm.getBBox());
              console.log(elm);
              a.push(elm);
            } else {
              break;
            }
          }
        }
      }
      this.highlightSVGelements(a);
    },
    highlightSVGelements(els) {
      for (const el of els) {
        el.attr('fill', '#22FFFF');
        console.log(el[0].getBBox());
        console.log(el.attr('transform'));
        let transform = el.attr('transform');
        if (transform) {
          transform = transform.substring(0, transform.length - 1);
          transform = transform.substring(7, transform.length);
          transform = transform.split(',');
          console.log(transform);
        }
        console.log($('.svg-pan-zoom_viewport').attr('transform'));
        let zptransform = $('.svg-pan-zoom_viewport').attr('transform');
        zptransform = zptransform.substring(0, zptransform.length - 1);
        zptransform = zptransform.substring(7, zptransform.length);
        zptransform = zptransform.split(',');
        console.log(zptransform);
        // const zpmsx = parseFloat(zptransform[0], 10);
        // const zpmsy = parseFloat(zptransform[3], 10);
        // const zpmx = parseInt(zptransform[4], 10);
        // const zpmy = parseInt(zptransform[5], 10);

        let emx;
        let emy;
        if (transform) {
          emx = parseInt(transform[4], 10);
          emy = parseInt(transform[5], 10);
        }
        // const emx = parseInt(transform[4], 10);
        // const emy = parseInt(transform[5], 10);

        let rx = emx;
        let ry = emy;
        // rx += (emx + 30) * zpmsx;
        // ry += (emy + 20) * zpmsy;
        if (transform) {
          const realZoom = this.panZoom.getSizes().realZoom;
          this.panZoom.pan({
            x: -(rx * realZoom) + (this.panZoom.getSizes().width / 2),
            y: -(ry * realZoom) + (this.panZoom.getSizes().height / 2),
          });
          this.panZoom.zoom(10);
          return;
        }
        rx += 100;
        ry += 100;
        // https://jsfiddle.net/Loymkgx8/2/

        // rx += 195;
        // ry += 210;
        rx -= 0;
        ry -= 0;
        setTimeout(() => {
          console.log(`doing zoom on ${rx} ${ry}`);
          this.panZoom.zoomAtPoint(20, {
            x: rx,
            y: ry,
          });
        }, 0);
      }
    },
    hlElements(event, compartmentID, ids) {
      if (ids && event) {
        this.ids = ids;
        this.loadSVG(compartmentID, this.swapSVG, this.getElement);
        // const a = this.getElement(ids);
      }
    },
    hlRow(tr) {
      const currentRow = tr;
      for (const row of tr.parentElement.getElementsByTagName('tr')) {
        row.classList.remove('sel-tr');
      }
      currentRow.classList.add('sel-tr');
    },
    searchElements() {
      const termsString = this.$refs.textarea.value;
      const arrayTerms = termsString.trim().split(',');
      const filterArray = [];
      for (let i = 0; i < arrayTerms.length; i += 1) {
        const trimTerm = arrayTerms[i].trim();
        if (trimTerm.length !== 0) {
          filterArray.push(trimTerm);
        }
      }
      this.getReactionComponentIDs(filterArray);
    },
    getReactionComponentIDs(array) {
      // get the correct IDs from the backend
      if (this.HLelms) {
        // un-highligh elements
        for (let i = 0; i < this.HLelms.length; i += 1) {
          this.HLelms[i].removeClass('hl');
        }
      }
      axios.post(`convert_to_reaction_component_ids/${this.compartmentID}`, { data: array })
      .then((response) => {
        const res = response.data;
        const d = {};
        for (let i = 0; i < res.length; i += 1) {
          const compartmentID = res[i][0];
          const id = res[i][1];
          if (!d[compartmentID.toString()]) {
            d[compartmentID.toString()] = [];
          }
          d[compartmentID.toString()].push(id);
        }
        this.results = d;
        this.showResults = this.results.length !== 0;
      })
      .catch(() => {});
    },
    getCompartmentFromCID,
  },
};
</script>

<style lang="scss">
#reporter-metabolites {
  #idarea {
    height: 2.5em;
  }

  #svg-wrapper {
    margin: auto;
    width: 100%;
  }

  #svgbox {
    position: relative;
    margin: auto;
    border: 1px solid black;
  }

  #svgOption {
    position: absolute;
    top: 10px;
    left: 10px;
    width: 80px;
    height: 30px;
    z-index: 10;

    span {
      display: inline-block;
      margin-right: 5px;
    }
  }

  #svgMissing {
    position: absolute;
    top: 10rem;
    left: 28rem;
    z-index: 10;
  }

  #table-res {
    margin-top: 1rem;
  }


  tr.m-tr {
    cursor: pointer;
    td {
        padding: 0.3em 0.5em;
    }
  }

  tr.sel-tr {
    background: #eee;
  }


  svg .hl {
    fill: #22FFFF;
  }
}

</style>
