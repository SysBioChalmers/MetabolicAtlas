<template>
  <div class="card" title="Click on any of the links to directly load a map">
    <header class="card-header has-text-centered">
      <p class="card-header-title has-text-primary has-text-weight-bold is-size-5">
        <span class="icon is-medium"><i class="fa fa-map-o"></i></span>&nbsp;
        <span>{{ messages.mapViewerName }}</span>
      </p>
    </header>
    <div v-if="mapAvailableLimited" class="card-content p-2">
      <table class="table test-table">
        <tbody>
          <tr v-for="customName in Object.keys(groupedMaps).sort()" :key="customName" class="m-3">
            <td>{{ customName }}</td>
            <td v-for="mapKey in ['2d', '3d']" :key="mapKey">
              <router-link v-if="groupedMaps[customName][mapKey] && viewerSelectedID"
                         :to="{ name: 'viewer',
                                params: { model: model.short_name, map_id: groupedMaps[customName][mapKey],
                                          reload: true },
                                query: { dim: mapKey, search: viewerSelectedID, sel: viewerSelectedID } }">
              {{ mapKey.toUpperCase() }}
              </router-link>
              <router-link v-else-if="groupedMaps[customName][mapKey]" :to="{ name: 'viewer',
              params: { model: model.short_name, map_id: groupedMaps[customName][mapKey]},
              query: { dim: mapKey } }">
              {{ mapKey.toUpperCase() }}
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
    mapAvailableLimited() {
      /* eslint-disable vue/no-side-effects-in-computed-properties */
      // TODO: move this into vuex
      if (Object.keys(this.mapsAvailable).length === 0) {
        return null;
      }
      const limited = JSON.parse(JSON.stringify(this.mapsAvailable)); // copy
      ['2d', '3d'].forEach((d) => {
        this.limitedMapsDim[d] = false;
        if (limited[d].compartment.length > this.mapLimitPerDim) {
          this.limitedMapsDim[d] = true;
          limited[d].compartment = limited[d].compartment.slice(0, this.mapLimitPerDim);
          limited[d].subsystem = [];
        } else {
          const remainingEntries = this.mapLimitPerDim - limited[d].compartment.length;
          if (limited[d].subsystem.length > remainingEntries) {
            limited[d].subsystem = limited[d].subsystem.slice(0, remainingEntries);
            this.limitedMapsDim[d] = true;
          }
        }
      });
      /* eslint-enable vue/no-side-effects-in-computed-properties */
      return limited;
    },
    mapKeys() {
      return ['2d', '3d'].filter(d => this.mapsAvailable[d].compartment.length > 0 || this.mapsAvailable[d].subsystem.length > 0);
    },
    groupedMaps() {
      const maps = {};
      const mapCopy = JSON.parse(JSON.stringify(this.mapsAvailable));
      ['2d', '3d'].forEach((d) => {
        mapCopy[d].compartment.forEach((c) => {
          if (!(c.customName in maps)) {
            maps[c.customName] = { '2d': '', '3d': '' };
          }
          maps[c.customName][d] = c.id;
        });
        mapCopy[d].subsystem.forEach((c) => {
          if (!(c.customName in maps)) {
            maps[c.customName] = { '2d': '', '3d': '' };
          }
          maps[c.customName][d] = c.id;
        });
      });
      return maps;
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
