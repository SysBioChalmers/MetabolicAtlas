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
import { default as EventBus } from '../../../event-bus';

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
      networkHistory: {},
      network: {
        nodes: [],
        links: [],
      },
    };
  },
  created() {
    EventBus.$off('show3Dnetwork');
    EventBus.$off('destroy3Dnetwork');
    EventBus.$off('update3DLoadedComponent');

    EventBus.$on('show3Dnetwork', (type, name) => {
      if (name.toLowerCase().substr(0, 7) === 'cytosol') {
        name = 'cytosol'; // eslint-disable-line no-param-reassign
      }
      if (this.loadedComponentType !== type ||
          this.loadedComponentName !== name ||
          this.emptyNetwork) {
        this.loadedComponentType = type;
        this.loadedComponentName = name;
        if (name in this.networkHistory) {
          this.$emit('loading');
          this.graph.graphData(this.networkHistory[name]);
        } else {
          this.getJson();
        }
      }
    });

    EventBus.$on('destroy3Dnetwork', () => {
      // console.log('quit 3D network');
      if (this.graph) {
        // this.graph.resetProps();
        // this.graph.null;
        this.graph.graphData({ nodes: [], links: [] });
        this.emptyNetwork = true;
      }
    });

    EventBus.$on('update3DLoadedComponent', (type, name) => {
      this.loadedComponentType = type;
      this.loadedComponentName = name;
    });
  },
  methods: {
    getJson() {
      this.$emit('loading');
      axios.get(`/${this.model.database_name}/json/${this.loadedComponentType}/${this.loadedComponentName}`)
        .then((response) => {
          this.network = response.data;
          setTimeout(() => {
            if (this.graph === null) {
              this.constructGraph();
            } else {
              this.graph.graphData(this.network);
            }
            this.emptyNetwork = false;
          }, 0);
        })
        .catch((error) => {
          this.$emit('loadComplete', false, error);
        });
    },
    constructGraph() {
      const width = this.$refs.graphParent.offsetParent.offsetWidth; // FIXME
      const height = this.$refs.graphParent.offsetParent.offsetHeight; // FIXME
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
        .cooldownTicks(0)
        .onEngineStop(() => {
          this.$emit('loadComplete', true, '');
          this.networkHistory[this.loadedComponentName] = this.network;
        });
    },
  },
};
</script>

<style lang="scss">

  #3d-graph {
    height: 100%;
    width:100%;
    overflow: hidden;
  }

</style>
