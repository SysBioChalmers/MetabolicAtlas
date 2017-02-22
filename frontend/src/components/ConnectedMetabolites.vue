<template>
  <div class="connected-metabolites">
    <h1>Connected metabolites</h1>
    <p>{{ $route.params.enzyme_id }}</p>
    <button v-on:click="load">Load something</button>
    <div v-if="loaded">
      {{response}}
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'connected-metabolites',
  data() {
    return {
      loaded: false,
      errorMessage: '',
      response: '',
    };
  },
  methods: {
    load() {
      axios.get(`enzymes/${this.$route.params.enzyme_id}/connected_metabolites`)
        .then((response) => {
          this.loaded = true;
          this.errorMessage = '';
          this.response = response;
        })
        .catch((error) => {
          this.loaded = true;
          this.errorMessage = error.message;
        });
    },
  },
  beforeMount() {
    this.load();
  },
};

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

h1, h2 {
  font-weight: normal;
}

</style>
