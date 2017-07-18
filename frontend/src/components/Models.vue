<template>
   <div v-if="errorMessage">
    {{ errorMessage }}
   </div>
  <div v-else>
    <span class="title">Models</span>
    <div v-for="m in GEMs">
    </div>
  </div>
</template>

<script>

import axios from 'axios';

export default {
  name: 'resources',
  data() {
    return {
      errorMessage: '',
      GEMs: [],
      oldMGEMs: [],
    };
  },
  methods: {
    getGEMs() {
      axios.get('gems/')
      .then((response) => {
        console.log(response);
        this.GEMs = response.data;
      })
      .catch(() => {
        this.errorMessage = this.$t('notFoundError');
      });
    },
    getOlGEMs() {
      axios.get('old_gems/')
      .then((response) => {
        this.oldMGEMs = response.data;
      })
      .catch(() => {
        this.errorMessage = this.$t('notFoundError');
      });
    },
  },
  beforeMount() {
    this.getGEMs();
    this.getOlGEMs();
  },
};

</script>

<style lang="scss">

.title {
  display: block;
  margin-bottom: 1rem;
}

.dsc, .name {
  height: 75px;
  line-height: 75px;

  span {
    display: inline-block;
    vertical-align: middle;
    line-height: normal;
  }
}

.name {
  font-size: 1.5rem;
}

</style>
