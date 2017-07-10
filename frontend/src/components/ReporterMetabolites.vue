<template>
  <div>
    <div class="column is-half">
      <div class="field">
        <div class="">
          <label class="label">IDs: </label>
        </div>
        <p class="control">
          <textarea class="textarea"></textarea>
        </p>
      </div>
    </div>
    <div>
      <button class="button is-primary">View</button>
    </div>
    <img src="assets/svg/nucleus_no_min.svg">
    <img src="../assets/whole_metabolic_network.png" width="200px">
    <div id="svg-wrapper" v-html="svgContent" style="width:600px; height:600px; border: 2px solid black">
      <object type="image/svg+xml" data="../assets/svg/nucleus_no_min.svg">
        Your browser does not support SVG
      </object>
      <object type="image/svg+xml" data="assets/svg/nucleus_no_min.svg2">
        Your browser does not support SVG
      </object>
    </div>
    <svg id="svg" style="width:100px; height:100px; border: 2px solid black"></svg>
  </div>
</template>

<script>

import { default as snap } from 'snapsvg';

export default {
  name: 'reporter-metabolites',
  data() {
    return {
      svgContent: '',
    };
  },
  mounted() {
    // Snap demo
    const s = snap('#svg');
    // Lets create big circle in the middle:
    const bigCircle = s.circle(150, 150, 100);
    // By default its black, lets change its attributes
    bigCircle.attr({
      fill: '#bada55',
      stroke: '#000',
      strokeWidth: 5,
    });
    console.log('Snap demo output:', bigCircle);

    /* eslint-disable global-require */
    const svgTest2 = require('assets/svg/nucleus_no_min.svg2');

    this.svgContent = svgTest2;

    console.log('start scaling');
    s.selectAll('path') // or whatever ID it has, or give it one
    .attr({ width: '100%', height: '100%', viewBox: '0 0 600 600' });

    s.selectAll('g') // or whatever ID it has, or give it one
    .attr({ width: '100%', height: '100%', viewBox: '0 0 600 600' });

    // Example for modifying network SVG
    setTimeout(() => {
      const s2 = snap('#svg-wrapper svg');
      s2.select('g').attr({
        fill: 'grey',
      });
    }, 0);
  },
  methods: {
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
