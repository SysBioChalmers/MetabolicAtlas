<template>
  <div class="container columns">
    <global-search
    ref="searchBar"
    :fastSearch=false
    :searchTerm=this.searchTerm></global-search>
  </div>
</template>

<script>
import axios from 'axios';
import GlobalSearch from 'components/GlobalSearch';

export default {
  name: 'search-table',
  components: {
    GlobalSearch,
  },
  data() {
    return {
      searchTerm: '',
      searchResults: [],
    };
  },
  methods: {
    startSearch() {
      axios.get(`search/${this.searchTerm}`)
      .then((response) => {
        this.searchResults = response.data;
      })
      .catch((error) => {
        this.searchResults = [];
        console.log(error);
      });
    },
  },
  beforeMount() {
    this.searchTerm = this.$route.query.term;
    console.log(this);
    console.log(this.$ref);
    console.log(this.$refs.searchBar);
    this.$refs.searchBar.search(this.searchTerm);
  },
};

</script>



<style lang="scss">
</style>
