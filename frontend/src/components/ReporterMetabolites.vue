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
          <button class="button is-primary">Switch SVG</button>
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
            <span class="button" v-show="!showMissingSVGString" v-on:click="panZoom.resetZoom()">RESET</span>
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
    };
  },
  mounted() {
    this.switchSVG(1, null);
  },
  methods: {
    superchargeSVG(callback) {
      // Example for modifying network SVG
      setTimeout(() => {
        this.snap = snap('#svg-wrapper svg');
        this.snap.attr({ width: '1200px' });
        this.snap.attr({ height: '700px' });
        // Example to allow panning and zooming
        this.panZoom = svgPanZoom('#svg-wrapper svg', {
          controlIconsEnabled: false, // got a reset button now
          fit: false, // if set to true => matrix(NaN) error
        });
        if (callback) {
          callback();
        }
      }, 0);
    },
    switchSVG(compartmentID, callback) {
      const newSvgName = getCompartmentFromCID(compartmentID).svgName;
      // const svgLink = `assets/svg/${newSvgName}.svg3`;
      if (!newSvgName) {
        // TODO remove this when all svg files available
        this.showMissingSVGString = true;
        this.svgContent = '';
        this.showLoader = false;
        return;
      }
      this.showMissingSVGString = false;
      if (newSvgName !== this.svgName) {
        // the following line doesn't work
        // this.svgContent = require(svgLink); // eslint-disable-line
        this.svgContent = require('assets/svg/ERtestwithid.svg2'); // raw string require works
        this.showLoader = true;
        this.svgName = newSvgName;
        // TODO pass width, height
        this.superchargeSVG(() => {
          callback();
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
        row.style.background = 'white';
      }
      currentRow.style.background = '#dbdbdb';
    },
    hlElements(event, compartmentID, ids) {
      const tr = event.srcElement.parentElement;
      this.hlRow(tr);
      this.switchSVG(compartmentID, () => {
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

        for (const type of ['Metabolite', 'Enzyme']) {
          for (let i = 0; i < ids.length; i += 1) {
            const id = ids[i].trim();
            console.log(`${type}_${id}`);
            let elm = this.snap.select(`${type}_${id}`);
            if (elm) {
              elm = elm.select('path');
              a.push(elm);
            }
            for (let j = 0; j < 1000; j += 1) {
              elm = this.snap.select(`${type}_${id}_${j}`);
              console.log(`${type}_${id}_${j}`);
              if (elm) {
                elm = elm.select('path');
                a.push(elm);
              } else {
                break;
              }
            }
          }
        }
        this.HLelms = a;
        if (this.HLelms) {
          for (let i = 0; i < this.HLelms.length; i += 1) {
            this.HLelms[i].addClass('hl');
          }
        }
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

.m-tr {
  cursor: pointer;
  td {
      padding: 0.3em 0.5em;
  }
}

svg .hl {
  fill: #22FFFF;
}

</style>
