<template>
  <div class="card" title="Click on any of the links to directly load a map">
    <header class="card-header has-text-centered">
      <p class="card-header-title has-text-primary has-text-weight-bold is-size-5">
        <span class="icon is-medium"><i class="fa fa-map-o"></i></span>&nbsp;
        <span>{{ messages.mapViewerName }}</span>
      </p>
    </header>
    <div v-if="mapsAvailable.length !== 0" class="card-content p-2">
      <table class="table test-table">
        <tbody>
          <tr v-for="component in mapsAvailable" :key="component.id">
            <td> {{ component.customName }} </td>
            <td v-if="component.svgMaps.length===0"> </td>
            <td v-else-if="component.svgMaps.length===1">
              <router-link :to="{ name: 'viewer',
                                  params: { model: model.short_name, map_id: component.svgMaps[0].id,
                                            reload: true },
                                  query: { dim: '2d', search: viewerSelectedID, sel: viewerSelectedID } }">
                2D
                </router-link>
            </td>
             <td v-else>
               <div class="select is-small is-link">
                <select @change="(e) => routeSelected2DMap(component.svgMaps, e.target.value)">
                  <option selected disabled>
                    2D
                  </option>
                  <option v-for="map in component.svgMaps" :key="map.id">
                    {{ map.customName }}
                  </option>
                </select>
              </div>
            </td>
            <td>
              <router-link :to="{ name: 'viewer',
                                  params: { model: model.short_name, map_id: component.id,
                                            reload: true },
                                  query: { dim: '3d', search: viewerSelectedID, sel: viewerSelectedID } }">
                3D
                </router-link>
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
    routeSelected2DMap(svgmaps, nameSelectedMap) {
      let svgId = '';
      svgmaps.forEach((map) => {
        if (map.customName === nameSelectedMap) {
          svgId = map.id;
        }
      });
      this.$router.push({ name: 'viewer',
        params: { model: this.model.short_name, map_id: svgId, reload: true },
        query: { dim: '2d', search: this.viewerSelectedID, sel: this.viewerSelectedID } });
    },
  },
};
</script>

<style lang="scss" scoped>
.card-content {
  overflow-y: auto;
  max-height: 400px;
}
</style>
