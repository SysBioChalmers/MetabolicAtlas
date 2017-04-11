<template>
  <div class="columns table-search">
    <div class="column field">
      <p class="control">
        <input
          v-model="term"
          @input="search"
          class="input"
          type="text"
          placeholder="Search in table"
        >
      </p>
    </div>
    <div class="column is-1">
      <a
        class="button is-pulled-right"
        @click="clearSearch()"
      >Reset</a>
    </div>
  </div>
</template>

<script>

export default {
  name: 'search-table',
  props: ['reset'],
  data() {
    return {
      term: '',
    };
  },
  methods: {
    clearSearch() {
      this.term = '';
      this.reset();
    },
    search() {
      this.$emit('search', this.term);
    },
  },
};

</script>

<style lang="sass">
</style>
