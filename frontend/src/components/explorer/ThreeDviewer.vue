<template>
  <div class="extended-section">
    <div id="iMainPanel" class="columns">
      <template v-if="errorMessage">
        <div class="column">
          <div class="columns">
            <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
              <p>{{ errorMessage }}</p>
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div id="viewer" class="atlas-viewer"></div>
      </template>
    </div>
  </div>
</template>

<script>

import { mapState } from 'vuex';
import { MetAtlasViewer } from '@metabolicatlas/mapviewer-3d';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'ThreeDViewer',
  props: {
    componentType: String,
    componentId: String,
    loading: Boolean,
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
    async componentType() {
      this.resetNetwork();
      await this.loadNetwork();
    },
    async componentId() {
      this.resetNetwork();
      await this.loadNetwork();
    },
  },
  async mounted() {
    // only load network for an entire model for this specific route
    if (this.$route.name === 'threeDviewerRoot') {
      await this.loadNetwork();
    }
  },
  methods: {
    async loadNetwork() {
      if (this.loading) {
        return; // prevent duplicate loads
      }

      this.$emit('loading');

      const payload = {
        model: this.model.apiName,
        version: this.model.apiVersion,
        type: this.componentType,
        id: this.componentId,
      };

      await this.$store.dispatch('maps/get3DMapNetwork', payload);
      this.renderNetwork();
      this.$emit('loadComplete', true, '');
      // console.log('controller:', controller);
      // controller.filterBy({group: 'm'});
      // controller.filterBy({id: [1, 2, 3, 4]});
      // Subscribe to node selection events
      // document.getElementById('viewer').addEventListener('select', e => console.debug('selected', e.detail));
    },
    renderNetwork() {
      this.controller = MetAtlasViewer('viewer');
      this.controller.setData(
        this.network,
        [{ group: 'e', sprite: '/sprite_round.png' },
          { group: 'r', sprite: '/sprite_square.png' },
          { group: 'm', sprite: '/sprite_triangle.png' }],
        15);
    },
    resetNetwork() {
      const viewer = document.getElementById('viewer');
      viewer.innerHTML = '';
    },
  },
};
</script>

<style lang='scss'>
.atlas-viewer {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}
</style>
