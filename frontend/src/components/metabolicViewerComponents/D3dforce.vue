<template>
  <div>
    <div ref="graphParent">
      <div id="3d-graph"></div>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import forceGraph3D from '3d-force-graph';
import { getCompartmentFromName } from '../../helpers/compartment';
import { default as EventBus } from '../../event-bus';

export default {
  name: 'd3dforce',
  props: [
    'model',
  ],
  data() {
    return {
      errorMessage: '',
      loadedComponentType: null,
      loadedComponentName: null,
      graph: null,
      emptyNetwork: true,
      network: {
        nodes: [],
        links: [],
      },
    };
  },
  created() {
    EventBus.$on('show3Dnetwork', (type, name) => {
      console.log('show 3D network');
      console.log(`emit ${type} ${name}`);
      if (name.toLowerCase().substr(0, 7) === 'cytosol') {
        name = 'cytosol'; // eslint-disable-line no-param-reassign
      }
      if (this.loadedComponentType !== type ||
          this.loadedComponentName !== name ||
          this.emptyNetwork) {
        this.loadedComponentType = type;
        this.loadedComponentName = name;
        this.getJson();
      }
    });
    EventBus.$on('destroy3Dnetwork', () => {
      console.log('quit 3D network');
      if (this.graph) {
        // this.graph.resetProps();
        // this.graph.null;
        this.graph.graphData({ nodes: [], links: [] });
        this.emptyNetwork = true;
      }
    });
  },
  methods: {
    getJson() {
      this.$emit('loading');
      axios.get(`/${this.model}/json/${this.loadedComponentType}/${this.loadedComponentName}`)
        .then((response) => {
          console.log(response);
          this.network = response.data;
          setTimeout(() => {
            if (this.graph === null) {
              this.constructGraph();
            } else {
              this.graph.graphData(this.network);
            }
            this.emptyNetwork = false;
            this.$emit('loadComplete', true, '');
          }, 0);
        })
        .catch((error) => {
          console.log(error);
          this.$emit('loadComplete', false, error);
        });
    },
    constructGraph() {
      const width = this.$refs.graphParent.offsetParent.offsetWidth; // FIXME
      const height = this.$refs.graphParent.offsetParent.offsetHeight; // FIXME
      console.log(`width ${width} ${height}`);
      this.graph = forceGraph3D()(document.getElementById('3d-graph'))
        .width(width).height(height)
        .nodeLabel('n')
        .linkSource('s')
        .linkTarget('t')
        .nodeAutoColorBy('g')
        .forceEngine('ngraph')
        .graphData({ nodes: this.network.nodes, links: this.network.links })
        // .linkAutoColorBy('group')
        .nodeAutoColorBy('g')
        .nodeOpacity(1)
        .linkWidth(2)
        .nodeResolution(8)
        .warmupTicks(100)
        .cooldownTicks(0);
    },
    getCompartmentFromName,
  },
};
</script>

<style lang="scss">

  #3d-graph {
    height: 100%;
  }

</style>
