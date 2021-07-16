<template>
  <div class="viewer-container">
    <div v-if="errorMessage" class="columns is-centered">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </div>
    <div v-else id="viewer3d"></div>
    <MapControls wrapper-elem-selector=".viewer-container" :is-fullscreen="isFullscreen"
                 :zoom-in="zoomIn" :zoom-out="zoomOut"
                 :toggle-full-screen="toggleFullscreen" :toggle-genes="toggleGenes"
                 :toggle-labels="toggleLabels"
                 :toggle-background-color="toggleBackgroundColor"
                 :style="{'z-index': network.nodes.length + 1}" />
    <MapSearch ref="mapsearch" :matches="searchedNodesOnMap"
               :fullscreen="isFullscreen" :style="{'z-index': network.nodes.length + 1}"
               @searchOnMap="searchIDsOnMap" @centerViewOn="centerElement"
               @unHighlightAll="unHighlight" />
    <MapLoader />
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import { MetAtlasViewer } from '@metabolicatlas/3d-network-viewer';
import { default as EventBus } from '@/event-bus';
import MapControls from '@/components/explorer/mapViewer/MapControls';
import MapLoader from '@/components/explorer/mapViewer/MapLoader';
import MapSearch from '@/components/explorer/mapViewer/MapSearch';
import { default as messages } from '@/helpers/messages';
import { default as colorToRGBArray } from '@/helpers/colors';

const NODE_TEXTURES = [
  { group: 'e', sprite: '/sprite_round.png' },
  { group: 'r', sprite: '/sprite_square.png' },
  { group: 'm', sprite: '/sprite_triangle.png' },
];

export default {
  name: 'ThreeDViewer',
  components: {
    MapControls,
    MapLoader,
    MapSearch,
  },
  props: {
    currentMap: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      errorMessage: '',
      messages,
      controller: null,
      isFullscreen: false,
      searchedNodesOnMap: [],
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      network: state => state.maps.network,
      selectedElement: state => state.maps.selectedElement,
      selectedElementId: state => state.maps.selectedElementId,
      backgroundColor: state => state.maps.backgroundColor,
      coords: state => state.maps.coords,
      dataOverlayPanelVisible: state => state.maps.dataOverlayPanelVisible,
    }),
    ...mapGetters({
      queryParams: 'maps/queryParams',
    }),
  },
  watch: {
    async currentMap() {
      this.resetNetwork();
      await this.loadNetwork();
    },
    dataOverlayPanelVisible() {
      // this is needed by the 3D viewer to update its size
      window.dispatchEvent(new Event('resize'));
    },
  },
  created() {
    EventBus.$off('apply3DHPARNAlevels');
    EventBus.$on('apply3DHPARNAlevels', this.applyColorsAndRenderNetwork);
  },
  async mounted() {
    await this.loadNetwork();
  },
  methods: {
    async loadNetwork() {
      this.$store.dispatch('maps/setLoading', true);

      const payload = {
        model: this.model.apiName,
        version: this.model.apiVersion,
        type: this.currentMap.type,
        id: this.currentMap.id,
      };
      await this.$store.dispatch('maps/get3DMapNetwork', payload);
      this.$store.dispatch('maps/setLoading', false);
      await this.applyColorsAndRenderNetwork({});
      // controller.filterBy({group: 'm'});
      // controller.filterBy({id: [1, 2, 3, 4]});
      // Subscribe to node selection events
      // document.getElementById('viewer').addEventListener('select', e => console.debug('selected', e.detail));
    },
    getElementIdAndType(element) {
      let type = 'metabolite';

      if (element.group === 'r') {
        type = 'reaction';
      } if (element.group === 'e') {
        type = 'gene';
      }

      return [element.id, type];
    },
    async renderNetwork(customizedNetwork) {
      this.resetNetwork();
      this.controller = MetAtlasViewer('viewer3d');

      const graphData = customizedNetwork || this.network;
      const nodeTypes = new Set(graphData.nodes.map(n => n.g));
      const nodeTextures = NODE_TEXTURES.filter(t => nodeTypes.has(t.group));

      this.controller.setNodeSelectCallback(this.selectElement);
      this.controller.setBackgroundColor(this.backgroundColor);
      this.controller.setUpdateCameraCallback(this.updateURLCoords);

      await this.controller.setData({
        graphData,
        nodeTextures,
        nodeSize: 10,
      });

      this.processURLQuery();
    },
    processURLQuery() {
      const { lx, ly, lz } = this.coords;
      this.controller.setCamera({ x: lx, y: ly, z: lz });

      const id = this.queryParams.sel;

      if (id) {
        setTimeout(async () => {
          await this.searchIDsOnMap([id]);
        }, 200);
      }
    },
    async selectElement(element) {
      const [id, type] = this.getElementIdAndType(element);
      const selectionData = { type, data: null, error: false };

      this.$emit('startSelection');
      try {
        this.$store.dispatch('maps/setLoadingElement', true);
        const payload = {
          model: this.model.apiName,
          version: this.model.apiVersion,
          type,
          id,
        };
        await this.$store.dispatch('maps/getSelectedElement', payload);
        const data = this.selectedElement;
        selectionData.data = data;
        this.$emit('updatePanelSelectionData', selectionData);
        this.$emit('endSelection', true);
        this.$store.dispatch('maps/setLoadingElement', false);
      } catch {
        this.$emit('updatePanelSelectionData', selectionData);
        this.$set(selectionData, 'error', true);
        this.$emit('endSelection', false);
        this.$store.dispatch('maps/setLoadingElement', false);
      }
    },
    async applyColorsAndRenderNetwork(levels) {
      const nodes = this.network.nodes.map((node) => {
        let color = colorToRGBArray('#9df');

        if (node.g === 'e') {
          if (Object.keys(levels).length === 0) {
            color = colorToRGBArray('#feb');
          } else {
            const partialID = node.id.split('-')[0];
            const key = levels[partialID] !== undefined ? partialID : 'n/a';
            color = colorToRGBArray(levels[key][0]);
          }
        }

        if (node.g === 'r') {
          color = colorToRGBArray('#fff');
        }

        if (node.g === 'm') {
          node.n = node.id; // eslint-disable-line
        }

        return {
          ...node,
          color,
        };
      });

      await this.renderNetwork({
        nodes,
        links: this.network.links,
      });
    },
    updateURLCoords({ x, y, z }) {
      const payload = {
        ...this.coords,
        lx: x,
        ly: y,
        lz: z,
      };
      this.$store.dispatch('maps/setCoords', payload);
    },
    resetNetwork() {
      const viewer = document.getElementById('viewer3d');
      viewer.innerHTML = '';
    },
    zoomIn() {
      this.zoomBy(50);
    },
    zoomOut() {
      this.zoomBy(-50);
    },
    zoomBy(amount) {
      const { lx, ly, lz } = this.coords;
      let z = lz - amount;
      if (z < 0) {
        z = 0;
      } else if (z > 1000) {
        z = 1000;
      }

      const payload = { x: lx, y: ly, z };
      this.controller.setCamera(payload);
      this.updateURLCoords(payload);
    },
    toggleFullscreen() {
      this.isFullscreen = !this.isFullscreen;
    },
    async toggleGenes() {
      await this.controller.toggleNodeType('e');
    },
    toggleLabels() {
      this.controller.toggleLabels();
    },
    toggleBackgroundColor() {
      this.$store.dispatch('maps/toggleBackgroundColor');
      this.controller.setBackgroundColor(this.backgroundColor);
    },
    async searchIDsOnMap(ids) {
      this.searchedNodesOnMap = [];

      if (ids && ids.length > 0) {
        this.searchedNodesOnMap = this.network.nodes
          .filter(n => ids.includes(n.id))
          .map(n => ({
            id: n.id,
            name: n.n,
            group: n.g,
          }));

        if (this.searchedNodesOnMap.length > 0) {
          await this.centerElement(this.searchedNodesOnMap[0]);
        }
      }
    },
    async centerElement(elem) {
      this.controller.selectBy({ id: elem.id });
      await this.selectElement(elem);
    },
    unHighlight() {
      this.searchedNodesOnMap = [];
      this.controller.selectBy({});
      this.$store.dispatch('maps/setSelectedElementId', null);
    },
  },
};
</script>

<style lang='scss' scoped>
.viewer-container, #viewer3d {
  width: 100%;
  height: 100%;
  @media screen and (max-width: $tablet) {
    height: $viewer-height;
  }
}
</style>
