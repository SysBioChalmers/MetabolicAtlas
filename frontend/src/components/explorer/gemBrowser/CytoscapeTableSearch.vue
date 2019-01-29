<template>
  <div class="columns table-search" style="margin-bottom: 0; padding-bottom: 0">
    <div class="column">
      <p class="control">
        <input v-model="term" @input="search"
          class="input" type="text" placeholder="Search in table">
      </p>
    </div>
    <div class="column is-1">
      <a :disabled="!isSearching" class="button" @click="clearSearch()">Reset</a>
    </div>
  </div>
</template>

<script>

export default {
  name: 'cytoscape-table-search',
  props: ['reset'],
  data() {
    return {
      term: '',
      isSearching: false,
    };
  },
  methods: {
    clearSearch() {
      this.term = '';
      this.reset();
      this.isSearching = false;
    },
    search() {
      this.$emit('search', this.term);
      if (this.term) {
        this.isSearching = true;
      } else {
        this.isSearching = false;
      }
    },
  },
};

</script>

<style lang="sass">

</style>
