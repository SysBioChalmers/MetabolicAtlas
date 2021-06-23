<template>
  <div class="card" title="Click on any of the links to directly load a map">
    <header class="card-header has-text-centered">
      <p class="card-header-title has-text-primary has-text-weight-bold is-size-5">
        <span class="icon is-medium"><i class="fa fa-map-o"></i></span>&nbsp;
        <span>{{ messages.mapViewerName }}</span>
      </p>
    </header>
    <div v-if="mapsAvailable.length !== 0" class="card-content p-2">
      <table class="table maps-table">
        <tbody class="has-text-left">
          <tr v-for="component in mapsAvailable" :key="component.id">
            <td> {{ component.customName }} </td>
            <td v-if="component.svgMaps.length===0"> </td>
            <td v-else-if="component.svgMaps.length===1">
              <button class="button is-outlined is-small link-button"
                      @click="routeSVGmap(component.svgMaps[0].id, '2d')">
                <span class="has-text-link"> 2D </span>
              </button>
            </td>
            <td v-else>
              <div class="select is-small">
                <select class="has-text-link" @change="(e) => routeSVGmap(e.target.value, '2d')">
                  <option selected disabled>
                    2D
                  </option>
                  <option v-for="map in component.svgMaps" :key="map.id" :value="map.id">
                    {{ map.customName }}
                  </option>
                </select>
              </div>
            </td>
            <td>
              <button class="button is-outlined is-small link-button"
                      @click="routeSVGmap(component.id, '3d')">
                <span class="has-text-link"> 3D </span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'MapsAvailable',
  props: {
    type: String,
    id: String,
    viewerSelectedID: String,
  },
  data() {
    return {
      messages,
      mapLimitPerDim: 4,
      limitedMapsDim: {
        '2d': false,
        '3d': false,
      },
      limited3DMaps: false,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      mapsAvailable: state => state.maps.availableMaps,
    }),
  },
  methods: {
    routeSVGmap(svgId, dimension) {
      const params = { model: this.model.short_name, map_id: svgId };
      const query = { dim: dimension };
      if (this.viewerSelectedID) {
        query.search = this.viewerSelectedID;
        query.sel = this.viewerSelectedID;
      }
      this.$router.push({ name: 'viewer', params, query });
    },
  },
};
</script>

<style lang="scss" scoped>
.card-content {
  overflow-y: auto;
  max-height: 400px;
}
.link-button {
  border-radius: 4px;
}
.table {
  width: 100%;
}
</style>
