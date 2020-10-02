<template>
  <div v-if="errorMessage" class="columns is-centered">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else id="viewer3d" class="fixed-height-desktop"></div>
</template>

<script>
import { mapState } from 'vuex';
import { MetAtlasViewer } from '@metabolicatlas/mapviewer-3d';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'ThreeDViewer',
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
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      network: state => state.maps.network,
    }),
  },
  watch: {
    async currentMap() {
      this.resetNetwork();
      await this.loadNetwork();
    },
  },
  async mounted() {
    await this.loadNetwork();
  },
  methods: {
    async loadNetwork() {
      const payload = {
        model: this.model.apiName,
        version: this.model.apiVersion,
        type: this.currentMap.type,
        id: this.currentMap.id,
      };
      await this.$store.dispatch('maps/get3DMapNetwork', payload);
      this.renderNetwork();
      // controller.filterBy({group: 'm'});
      // controller.filterBy({id: [1, 2, 3, 4]});
      // Subscribe to node selection events
      // document.getElementById('viewer').addEventListener('select', e => console.debug('selected', e.detail));
    },
    renderNetwork() {
      this.controller = MetAtlasViewer('viewer3d');
      this.controller.setData(
        this.network,
        [{ group: 'e', sprite: '/sprite_round.png' },
          { group: 'r', sprite: '/sprite_square.png' },
          { group: 'm', sprite: '/sprite_triangle.png' }],
        15);
    },
    resetNetwork() {
      const viewer = document.getElementById('viewer3d');
      viewer.innerHTML = '';
    },
  },
};
</script>

<style lang='scss'>
#viewer3d {
  width: 100%;
  height: 100%;
}
</style>
