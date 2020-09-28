<template>
  <div>
    <div v-for="category in Object.keys(mapsListing).sort()" :key="category">
      <p class="is-capitalized is-size-6 has-text-weight-bold">{{ category }}</p>
      <span v-for="item in mapsListing[category]" :key="item.id">
        <template v-if="showing2D">
          <template v-if="item.svgs.length === 0">
            {{ item.name }}
          </template>
          <template v-else-if="item.svgs.length === 1">
            <a @click="changeToMap(item.svgs[0].id)">
              {{ item.svgs[0].customName }}
            </a>
          </template>
          <template v-else>
            {{ item.name }}:
            <a v-for="svg in item.svgs" :key="svg.id" @click="changeToMap(svg.id)">
              {{ svg.customName }}
            </a>
          </template>
        </template>
        <template v-else>
          <a @click="changeToMap(item.id)">
            {{ item.name }}
          </a>
        </template>
        <br>
      </span>
      <br>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'MapsListing',
  props: {
    mapsListing: {
      type: Object,
      required: true,
    },
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      showing2D: state => state.maps.showing2D,
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
