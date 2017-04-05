<template>
  <div class="reactome">
    <h3 class="title is-3">Reactome</h3>
    <div class="container">
      <div id="diagram"></div>
    </div>
  </div>
</template>

<script>

import SVG from 'svg.js';
import 'svg.connectable.js';
import 'svg.draggy.js';
// import { chemicalFormula, chemicalName, chemicalNameLink } from '../helpers/chemical-formatters';

export default {
  name: 'reactome',
  data() {
    return {
      errorMessage: '',
    };
  },
  mounted() {
    const diagram = new SVG('diagram').size('100%', 500);

    const links = diagram.group();
    const markers = diagram.group();
    const nodes = diagram.group();

    const g1 = nodes.group().translate(100, 200).draggy();
    g1.ellipse(100, 50).fill('#C2185B');

    const g2 = nodes.group().translate(300, 200).draggy();
    g2.ellipse(100, 50).fill('#E91E63');

    const g3 = nodes.group().translate(500, 200).draggy();
    g3.ellipse(100, 50).fill('#FF5252');
    g3.plain('result');

    g1.connectable({
      container: links,
      markers,
    }, g2).setLineColor('#5D4037');

    g2.connectable({
      padEllipse: true,
    }, g3).setLineColor('rgba(0, 0, 0, 0)');

    g2.connectable({
      padEllipse: true,
    }, g3).setLineColor('#5D4037');
  },
};

</script>

<style lang="scss">

</style>
