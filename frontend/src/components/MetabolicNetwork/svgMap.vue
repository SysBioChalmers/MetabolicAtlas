<template>
  <div>
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
</template>
<script>

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
  methods: {
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

<style lang="scss" scoped>

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

  svg .hl {
    fill: #22FFFF;
  }
</style>
