<template>
  <div class="card">
    <header class="card-header has-text-centered">
      <p class="card-header-title has-text-primary has-text-weight-bold is-size-5">
        <span class="icon is-medium"><i class="fa fa-map-o"></i></span>&nbsp;
        <span>{{ messages.mapViewerName }}</span>
      </p>
      <a href="#" class="card-header-icon" aria-label="more options">
      </a>
    </header>
    <div class="card-content" style="padding: 0.5rem;">
      <div class="content has-text-left is-paddingless" v-if="Object.keys(mapsAvailable).length !== 0">
        <ul v-if="mapsAvailable['2d']['count'] !== 0"> 2D maps
          <template v-for="map in mapsAvailable['2d']['compartment']">
            <li><router-link  :to="{ path: `/explore/map-viewer/${model.database_name}/${map[2]}/${map[0]}/${elementID}?dim=2d` }">
              {{ map[1] }}
            </router-link></li>
          </template>
          <template v-for="map in mapsAvailable['2d']['subsystem']">
            <li><router-link  :to="{ path: `/explore/map-viewer/${model.database_name}/${map[2]}/${map[0]}/${elementID}?dim=2d` }">
              {{ map[1] }}
            </router-link></li>
          </template>
        </ul>
        <ul v-if="mapsAvailable['3d']['count'] !== 0">3D maps
           <template v-for="map in mapsAvailable['3d']['compartment']">
            <li><router-link :to="{ path: `/explore/map-viewer/${model.database_name}/${map[2]}/${map[0]}/${elementID}?dim=3d` }">
              {{ map[1] }}
            </router-link></li>
          </template>
          <template v-for="map in mapsAvailable['3d']['subsystem']">
            <li><router-link :to="{ path: `/explore/map-viewer/${model.database_name}/${map[2]}/${map[0]}/${elementID}?dim=3d` }">
              {{ map[1] }}
            </router-link></li>
          </template>
        </ul>
      </div>
    </div>
    <footer class="card-footer">
    </footer>
  </div>
</template>

<script>
import axios from 'axios';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'maps-available',
  props: ['model', 'type', 'id', 'elementID'],
  data() {
    return {
      mapsAvailable: {},
      messages,
    };
  },
  created() {
    this.getAvailableMaps();
  },
  methods: {
    getAvailableMaps() {
      axios.get(`${this.model.database_name}/available_maps/${this.type}/${this.id}`)
      .then((response) => {
        this.mapsAvailable = response.data;
      }).catch(() => {
      });
    },
  },
};
</script>

<style lang="scss">
</style>
