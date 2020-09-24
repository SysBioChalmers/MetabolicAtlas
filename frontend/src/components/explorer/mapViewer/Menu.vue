<template>
  <div>
    <a class="button" @click="changeDimension()">
      Switch to {{ showing2D ? '3D' : '2D ' }}
    </a>
    <a class="button" @click="showingMapListing = !showingMapListing">
      {{ showingMapListing ? 'Hide' : 'Show' }} map list
    </a>
    <MapsListing v-if="showingMapListing" />
  </div>
</template>

<script>
import { mapState } from 'vuex';
import MapsListing from '@/components/explorer/mapViewer/MapsListing.vue';

export default {
  name: 'Menu',
  components: {
    MapsListing,
  },
  data() {
    return {
      showingMapListing: true,
    };
  },
  computed: {
    ...mapState({
      showing2D: state => state.maps.showing2D,
    }),
  },
  methods: {
    changeDimension() {
      this.$store.dispatch('maps/setShowing2D', !this.showing2D);
    },
  },
};
</script>

<style lang="scss"></script>
