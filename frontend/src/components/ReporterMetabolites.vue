<template>
  <div>
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
        <loader v-show="showLoader"></loader>
        <div v-show="!showLoader" id="svgbox">
          <div id="svg-wrapper" v-html="svgContent">
          </div>
          <div id="svgOption">
            <span class="button" v-show="!showMissingSVGString" v-on:click="panZoom.reset()">RESET</span>
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

import { default as snap } from 'snapsvg';
// import zpd from 'snap.svg.zpd';
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
      snap: null,
      zoomBox: {
        minX: 99999,
        maxX: 0,
        minY: 99999,
        maxY: 0,
      },
    };
  },
  mounted() {
    this.switchSVG(1, null);
  },
  methods: {
    superchargeSVG(callback) {
      // Example for modifying network SVG
      setTimeout(() => {
        console.log('load snap');
        this.snap = snap('#svg-wrapper svg');
        // this.snap.attr({ width: '1200px' });
        // this.snap.attr({ height: '700px' });
        console.log('load snap finished');

        // Example to allow panning and zooming
        // svgPanZoom('#svg-wrapper svg').destroy();
        if (callback) {
          callback();
        }
      }, 0);
    },
    switchSVG(compartmentID, callback) {
      const newSvgName = getCompartmentFromCID(compartmentID).svgName;
      const svgLink = `${window.location.origin}/svgs/${newSvgName}.svg`;
      if (!newSvgName) {
        // TODO remove this when all svg files available
        this.showMissingSVGString = true;
        this.svgContent = '';
        this.showLoader = false;
        return;
      }
      this.showMissingSVGString = false;
      if (newSvgName !== this.svgName) {
        axios.get(svgLink)
          .then((response) => {
            this.svgContent = response.data;
            this.showLoader = true;
            this.svgName = newSvgName;
            // TODO pass width, height
            this.superchargeSVG(() => {
              if (callback) {
                callback();
              }
              this.showLoader = false;
            });
          })
          .catch((error) => {
            // TODO: handle error
            console.log(error);
            this.showLoader = false;
          });
      } else {
        callback();
        this.showLoader = false;
      }
    },
    hlRow(tr) {
      const currentRow = tr;
      for (const row of tr.parentElement.getElementsByTagName('tr')) {
        row.classList.remove('sel-tr');
      }
      currentRow.classList.add('sel-tr');
    },
    updateZoomBox(elBox) {
      if (elBox.x < this.zoomBox.minX) {
        this.zoomBox.minX = elBox.x;
      }
      if (elBox.x > this.zoomBox.maxX) {
        this.zoomBox.maxX = elBox.x;
      }
      if (elBox.y < this.zoomBox.minY) {
        this.zoomBox.minY = elBox.y;
      }
      if (elBox.y > this.zoomBox.maxY) {
        this.zoomBox.maxY = elBox.y;
      }

      const debug = false;
      if (debug) {
        this.zoomBox.minX = 77.9296875;
        this.zoomBox.maxX = 77.9296875;
        this.zoomBox.minY = 17412.85586262676;
        this.zoomBox.maxY = 17412.85586262676;
      }

      console.log('new zoomBox');
      console.log(this.zoomBox);
    },
    zoomInBox() {
      // const realZoom = this.panZoom.getSizes().realZoom;
      const nx = this.zoomBox.minX + ((this.zoomBox.maxX - this.zoomBox.minX) / 2);
      const ny = this.zoomBox.minY + ((this.zoomBox.maxY - this.zoomBox.minY) / 2);
      // nx = 100;
      // ny = 100;
      console.log(this.panZoom.getSizes());
      console.log(`zoomto nx: ${nx} | ny: ${ny}`);
      // this.panZoom.pan({ x: 500, y: 500 });
      // this.panZoom.fit();
      this.panZoom.zoomAtPoint(1, {
        x: nx,
        y: ny,
      });
    },
    hlElements(event, compartmentID, ids) {
      const tr = event.srcElement.parentElement;

      this.hlRow(tr);
      this.switchSVG(compartmentID, () => {
        setTimeout(() => {
          console.log('load pan zoom');
          this.panZoom = svgPanZoom('#svg-wrapper svg', {
            minZoom: 0.01,
            maxZoom: 50,
            zoomScaleSensitivity: 0.6,
            onZoom: function f() {
              console.log(`rz: ${this.getSizes().realZoom} | zoom ${this.getZoom()}`);
            },
          });
          // this.panZoom.fit();
          console.log('load pan zoom finished');
          const a = [];
          // select using class
          /*
          for (let i = 0; i < ids.length; i += 1) {
            const id = ids[i].trim();
            const elms = this.snap.selectAll(`.${id}`);  // rcID should be assign to class attribut
            for (let j = 0; j < elms.length; j += 1) {
              a.push(elms[j]);
            }
          }
          */
          // select by id: <g class="Metabolite" id="Metabolite$E_3131$0" name="E_3131">
          // not $ have been replaced by _

          // debug
          const debug = true;
          if (ids) {
            console.log('debug');
          }
          const ids2 = ['M_m03052r'];

          for (const type of ['Metabolite', 'Enzyme']) {
            for (let i = 0; i < ids2.length; i += 1) {
              const id = ids2[i].trim();
              let elm = this.snap.select(`#${type}_${id}`);
              if (elm) {
                elm = elm.select('path');
                if (debug) {
                  console.log(`${type}_${id} box : ${elm.getBBox()}`);
                }
                this.updateZoomBox(elm.getBBox());
                a.push(elm);
              }
              for (let j = 2; j < 3; j += 1) {
                elm = this.snap.select(`#${type}_${id}_${j}`);
                if (debug) {
                  console.log(`${type}_${id}_${j}`);
                }
                if (elm) {
                  elm = elm.select('path');
                  if (debug) {
                    console.log(`${type}_${id}_${j} box : ${elm.getBBox()}`);
                    elm.click(function f() {
                      console.log(this);
                      console.log(this.element.getTransformToElement(this.svgContent));
                    });
                  }
                  this.updateZoomBox(elm.getBBox());
                  console.log(elm.matrix);
                  a.push(elm);
                } else {
                  break;
                }
              }
            }
          }
          console.log(this.zoomBox);
          this.HLelms = a;
          if (this.HLelms) {
            console.log('elms found');
            console.log(this.HLelms.length);
            for (let i = 0; i < this.HLelms.length; i += 1) {
              this.HLelms[i].addClass('hl');
            }
            this.zoomInBox();
          }
        }, 0);
        // this.panZoom.fit(); //do not worj with snap
      });
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

#idarea {
  width: 100px;
  height: 200px;
}

#svg-wrapper {
  margin: auto;
  width: 100%;
  img {
    padding: 20px;
    width: 600px;
    margin: auto;
  }
}

#svgbox {
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

</style>
