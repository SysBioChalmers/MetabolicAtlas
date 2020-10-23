<template>
  <div class="card" title="Click on any of the links to directly load a map">
    <header class="card-header has-text-centered">
      <p class="card-header-title has-text-primary has-text-weight-bold is-size-5">
        <span class="icon is-medium"><i class="fa fa-map-o"></i></span>&nbsp;
        <span>{{ messages.mapViewerName }}</span>
      </p>
    </header>
    <div v-if="mapAvailableLimited" class="card-content pl-3 py-2 pr-2">
      <div v-for="mapKey in mapKeys" :key="mapKey"
           class="content has-text-left px-0 py-0">
        <template>
          <div>{{ mapKey.toUpperCase() }} maps</div>
          <ul class="py-0 px-4">
            <template v-for="mapType in Object.keys(mapAvailableLimited[mapKey])">
              <template v-for="map in mapAvailableLimited[mapKey][mapType]">
                <li :key="map.id">
                  <router-link v-if="viewerSelectedID"
                               :to="{ name: 'viewer',
                                      params: { model: model.short_name, type: mapType, map_id: map.id, reload: true },
                                      query: { dim: mapKey, search: viewerSelectedID, sel: viewerSelectedID } }">
                    {{ map.customName }}
                  </router-link>
                  <router-link v-else :to="{ name: 'viewer',
                                             params: { model: model.short_name, type: mapType, map_id: map.id},
                                             query: { dim: mapKey } }">
                    {{ map.customName }}
                  </router-link>
                </li>
              </template>
            </template>
            <!-- eslint-disable-next-line max-len -->
            <li v-if="limitedMapsDim[mapKey]" class="clickable" title="View all maps" @click="mapLimitPerDim = 1000">...</li>
          </ul>
        </template>
      </div>
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
  },
};
</script>

<style lang="scss" scoped>
.card-content {
  overflow-y: auto;
  max-height: 400px;
}
</style>
