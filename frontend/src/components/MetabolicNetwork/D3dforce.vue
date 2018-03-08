<template>
  <div>
    <loader v-show="showLoader"></loader>
    <div v-show="!showLoader">
      <div id="3d-graph"></div>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import Loader from 'components/Loader';
import forceGraph3D from '3d-force-graph';
import { getCompartmentFromName } from '../../helpers/compartment';

export default {
  name: 'd3dforce',
  components: {
    Loader,
  },
  data() {
    return {
      errorMessage: '',
      compartment: null,
      subsystem: null,
      showLoader: false,
      network: null,
    };
  },
  mounted() {
    const Graph = forceGraph3D()(document.getElementById('3d-graph'));
    const dataSet = this.getGraphDataSet();
    Graph.resetProps(); // Wipe current state
    dataSet(Graph); // Load data set
  },
  methods: {
    getJson() {
      axios.get('/')
        .then((response) => {
          console.log(response);
          setTimeout(() => {
            this.showLoader = false;
          }, 0);
        })
        .catch((error) => {
          console.log(error);
          this.showLoader = false;
        });
    },
    getGraphDataSet() {
      const tunnel = function graph(Graph) {
        Graph
          .nodeLabel('name')
          .nodeAutoColorBy('group')
          .forceEngine('ngraph')
          .graphData({ nodes: this.network.nodes, links: this.network.links })
          .linkAutoColorBy('group')
          .nodeAutoColorBy('group')
          .nodeOpacity(1)
          .linkWidth(0)
          .nodeResolution(8)
          .cooldownTime(120000);
      };
      tunnel.description = '';
      return tunnel;
    },
    getCompartmentFromName,
  },
};
</script>

<style lang="scss">

</style>
