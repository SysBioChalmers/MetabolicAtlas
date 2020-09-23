<template>
  <div>
    <a class="button" @click="changeDimension()">
      Switch to {{ showing2D ? '3D' : '2D ' }}
    </a>
    <a class="button" @click="showingMapListing = !showingMapListing">
      {{ showingMapListing ? 'Hide' : 'Show'}} map list
    </a>
    <template v-if="showingMapListing">
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
    </template>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';

export default {
  name: 'Menu',
  props: {
    mapsListing: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      showingMapListing: true,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      showing2D: state => state.maps.showing2D,
    }),
    ...mapGetters({
      queryParams: 'maps/queryParams',
    }),
  },
  methods: {
    changeToMap(newMapId) {
      this.$router.push({ params: { map_id: newMapId }, query: { dim: '2d' } });
    },
    changeDimension() {
      this.$store.dispatch('maps/setShowing2D', !this.showing2D);
    },
  },
};
</script>

<style lang="scss"></script>
