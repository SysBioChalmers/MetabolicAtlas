<template>
  <div class="viewer-container">
    <div v-if="errorMessage" class="columns is-centered">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </div>
    <div v-else id="viewer3d"></div>
    <MapControls :is-fullscreen="isFullscreen" :zoom-in="zoomIn" :zoom-out="zoomOut"
                 :toggle-full-screen="toggleFullScreen" :toggle-genes="toggleGenes" />
    <MapLoader :loading="showLoader" />
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { MetAtlasViewer } from '@metabolicatlas/mapviewer-3d';
import { default as EventBus } from '@/event-bus';
import MapControls from '@/components/explorer/mapViewer/MapControls';
import MapLoader from '@/components/explorer/mapViewer/MapLoader';
import { default as messages } from '@/helpers/messages';
import { default as colorToRGBArray } from '@/helpers/colors';

export default {
  name: 'ThreeDViewer',
  components: {
    MapControls,
    MapLoader,
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
      showLoader: true,
      isFullscreen: false,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      network: state => state.maps.network,
      selectedElement: state => state.maps.selectedElement,
      selectedElementId: state => state.maps.selectedElementId,
    }),
  },
  watch: {
    async currentMap() {
      this.resetNetwork();
      await this.loadNetwork();
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
      this.showLoader = true;

      const payload = {
        model: this.model.apiName,
        version: this.model.apiVersion,
        type: this.currentMap.type,
        id: this.currentMap.id,
      };
      await this.$store.dispatch('maps/get3DMapNetwork', payload);
      this.renderNetwork();
      this.showLoader = false;
      // controller.filterBy({group: 'm'});
      // controller.filterBy({id: [1, 2, 3, 4]});
      // Subscribe to node selection events
      // document.getElementById('viewer').addEventListener('select', e => console.debug('selected', e.detail));
    },
    getElementIdAndType(element) {
      if (element.group === 'r') {
        return [element.id, 'reaction'];
      } if (element.group === 'e') {
        return [element.id.split('-')[0], 'gene'];
      }
      return [element.id.split('-')[0], 'metabolite'];
    },
    renderNetwork(customizedNetwork) {
      this.resetNetwork();
      this.controller = MetAtlasViewer('viewer3d');
      this.controller.setData({
        graphData: customizedNetwork || this.network,
        nodeTextures: [
          { group: 'e', sprite: '/sprite_round.png' },
          { group: 'r', sprite: '/sprite_square.png' },
          { group: 'm', sprite: '/sprite_triangle.png' },
        ],
        nodeSize: 15,
      });
      this.controller.setNodeSelectCallback(this.selectElement);
      this.controller.setBackgroundColor('#222');
    },
    async selectElement(element) {
      const [id, type] = this.getElementIdAndType(element);
      const selectionData = { type, data: null, error: false };

      this.$emit('startSelection');
      try {
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
      } catch {
        this.$emit('updatePanelSelectionData', selectionData);
        this.$set(selectionData, 'error', true);
        this.$emit('endSelection', false);
      }
    },
    applyColorsAndRenderNetwork(levels) {
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

        return {
          ...node,
          color,
        };
      });

      this.renderNetwork({
        nodes,
        links: this.network.links,
      });
    },
    resetNetwork() {
      const viewer = document.getElementById('viewer3d');
      viewer.innerHTML = '';
    },
    zoomIn() {
      console.log('zoom in');
    },
    zoomOut() {
      console.log('zoom out');
    },
    toggleFullScreen() {
      console.log('toggle fullscreen');
    },
    toggleGenes() {
      this.controller.toggleNodeType('e');
    },
  },
};
</script>

<style lang='scss' scoped>
.viewer-container, #viewer3d {
  width: 100%;
  height: 100%;
}
</style>
