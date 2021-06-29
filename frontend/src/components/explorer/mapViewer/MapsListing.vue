<template>
  <div id="maps-listing">
    <div v-for="category in categories"
         :key="category" class="card my-3">
      <p class="is-capitalized is-size-6 has-text-weight-bold">{{ category.replace(/.$/," maps") }}</p>
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
            <a v-for="svg in [...item.svgs].sort((a, b) => a.customName.localeCompare(b.customName))"
               :key="svg.id" class="inline" @click="changeToMap(svg.id)">
              {{ svg.customName }}
            </a>
          </template>
        </template>
        <template v-else>
          <a @click="changeToMap(item.id)">
            {{ item.name }}
          </a>
        </template>
      </span>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'MapsListing',
  computed: {
    ...mapState({
      model: state => state.models.model,
      showing2D: state => state.maps.showing2D,
      mapsListing: state => state.maps.mapsListing,
    }),
    categories() {
      return Object.keys(this.mapsListing).filter(c => this.mapsListing[c].length > 0 && (c !== 'customs' || this.showing2D)).sort();
    },
  },
  methods: {
    changeToMap(newMapId) {
      this.$router.push({ params: { map_id: newMapId }, query: { dim: this.showing2D ? '2d' : '3d' } });
    },
  },
};
</script>

<style lang="scss">

#maps-listing {
  p, span {
    padding: 0.5rem 1rem;
  }

  span {
    display: block;
    color: rgba(0, 84, 158, 0.5);

    a:not(.inline) {
      display: block;
    }

    &:nth-child(even) {
      background-color: rgba(211, 211, 211, 0.18);
    }

    &:nth-child(odd) {
      background-color: rgba(211, 211, 211, 0.08);
    }
  }
}

</style>
