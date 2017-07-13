<template>
  <div>
    <div class="columns">
      <div class="column is-half">
        <div class="field">
          <div class="">
            <label class="label">IDs: </label>
          </div>
          <p class="control">
            <textarea class="textarea" ref="textarea" placeholder="udp, h2o2, sam, m_m01784n"></textarea>
          </p>
        </div>
      </div>
      <div class="column">
        <button class="button is-primary" @click="highLightElements">Highlight</button>
      </div>
    </div>
    <div id="svg-wrapper" v-html="svgContent" style="width:1200px; height:1200px; border: 2px solid black">
      <object type="image/svg+xml" data="../assets/svg/nucleus_no_min.svg">
        Your browser does not support SVG
      </object>
      <object type="image/svg+xml" data="assets/svg/nucleus_no_min.svg2">
        Your browser does not support SVG
      </object>
    </div>
  </div>
</template>

<script>

import { default as snap } from 'snapsvg';
import axios from 'axios';
import svgPanZoom from 'svg-pan-zoom';

export default {
  name: 'reporter-metabolites',
  data() {
    return {
      svgContent: '',
      compartmentID: 8, // TODO make it dynamic
      HLColor: '#22FFFF',
    };
  },
  mounted() {
    /* eslint-disable global-require */
    // this.svgContent = require('assets/svg/ER.id_added.svg2');
    this.svgContent = require('assets/svg/nucleus_no_min.svg2');

    // Example for modifying network SVG
    setTimeout(() => {
      const s = snap('#svg-wrapper svg');
      s.attr({ width: '1200px' });
      s.attr({ height: '1200px' });

      // Example to allow panning and zooming
      svgPanZoom('#svg-wrapper svg', {
        controlIconsEnabled: true,
      });

      // console.log(s.select('path').transform());
      // console.log(s.selectAll('path'));

      /* s.selectAll('path') // or whatever ID it has, or give it one
      .attr({ width: '100%', height: '100%', viewBox: '0 0 600 600' });

      s.selectAll('g') // or whatever ID it has, or give it one
      .attr({ width: '100%', height: '100%', viewBox: '0 0 600 600' }); */
    }, 0);
  },
  methods: {
    highLightElements() {
      const termsString = this.$refs.textarea.value;

      const arrayTerms = termsString.trim().split(',');
      const filterArray = [];
      for (let i = 0; i < arrayTerms.length; i += 1) {
        const trimTerm = arrayTerms[i].trim();
        if (trimTerm.length !== 0) {
          filterArray.push(trimTerm);
        }
      }
      this.hlReactionComponentIDs(filterArray);
    },
    hlReactionComponentIDs(array) {
      // get the correct IDs from the backend
      axios.get(`convert_to_reaction_component_ids/${this.compartmentID}/${array.join(',')}`)
      .then((response) => {
        const result = response.data;
        const s = snap('#svg-wrapper svg');
        for (let i = 0; i < result.length; i += 1) {
          const id = result[i].trim();
          const elms = s.selectAll(`.${id}`);  // rcID should be assign to class attribut
          for (let j = 0; j < elms.length; j += 1) {
            elms[j].attr({ fill: this.HLColor });
          }
        }
      })
      .catch(() => {});
    },
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

</style>
