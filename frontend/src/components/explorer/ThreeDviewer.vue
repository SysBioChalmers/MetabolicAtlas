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
import { default as EventBus } from '@/event-bus';
import { default as messages } from '@/helpers/messages';
import { default as colorToRGBArray } from '@/helpers/colors';

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
      await this.loadNetwork();
    },
    async componentId() {
      await this.loadNetwork();
    },
  },
  created() {
    EventBus.$off('apply3DHPARNAlevels');
    EventBus.$on('apply3DHPARNAlevels', this.applyColorsAndRenderNetwork);
  },
  async mounted() {
    if (this.$route.name === 'threeDviewerRoot'
      || (this.componentType && this.componentId)
    ) {
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
      this.applyColorsAndRenderNetwork({});
      this.$emit('loadComplete', true, '');
      // console.log('controller:', controller);
      // controller.filterBy({group: 'm'});
      // controller.filterBy({id: [1, 2, 3, 4]});
      // Subscribe to node selection events
      // document.getElementById('viewer').addEventListener('select', e => console.debug('selected', e.detail));
    },
    renderNetwork(customizedNetwork) {
      this.resetNetwork();
      this.controller = MetAtlasViewer('viewer');
      this.controller.setData(
        customizedNetwork || this.network,
        [{ group: 'e', sprite: '/sprite_round.png' },
          { group: 'r', sprite: '/sprite_square.png' },
          { group: 'm', sprite: '/sprite_triangle.png' }],
        15);
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
      const viewer = document.getElementById('viewer');
      viewer.innerHTML = '';
    },
  },
};
</script>

<style lang='scss'>
.atlas-viewer {
  margin: 0;
  padding: 0;
}
</style>
