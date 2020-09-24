<template>
  <div id="mapList">
    <div v-for="category in Object.keys(mapsListing).sort()" :key="category">
      <p class="is-capitalized is-size-6 has-text-weight-bold">{{ category }}</p>
      <span v-for="item in mapsListing[category]" :key="item.id">
        <template v-if="showing2D">
          <a v-for="svg in item.svgs" :key="svg.id" @click="changeToMap(item.id)">
            {{ svg.customName }}<br>
          </a>
        </template>
        <template v-else>
          <a @click="changeToMap(item.id)">
            {{ item.name }}<br>
          </a>
        </template>
      </span>
      <br>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';

export default {
  name: 'MapsListing',
  computed: {
    ...mapState({
      model: state => state.models.model,
      showing2D: state => state.maps.showing2D,
    }),
    ...mapGetters({
      mapsListing: 'maps/mapsListing',
    }),
  },
  methods: {
    changeToMap(newMapId) {
      this.$router.push({ params: { map_id: newMapId }, query: { dim: this.showing2D ? '2d' : '3d' } });
    },
  },
};
</script>

<style lang="scss"></script>
