<template>
  Helloe
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else class="subsystem-table">
    <table v-if="info && Object.keys(info).length != 0" class="table main-table">
      <tr class="m-row" v-for="reaction in reactions">
        <td class="td-key">Reaction</td>
        <td v-html="reaction.id"></td>
      </tr>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'subsystem',
  data() {
    return {
      sId: this.$route.query.id,
      ann: {},
      metabolites: [],
      enzymes: [],
      reactions: [],
      errorMessage: '',
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  methods: {
    setup() {
      this.sId = this.$route.query.id;
      this.load();
    },
    load() {
      axios.get(`showsubsystem/${this.sId}/`)
      .then((response) => {
        this.ann = response.data.subsystemAnnotations;
        this.metabolites = response.data.metabolites;
        this.enzymes = response.data.enzymes;
        this.reactions = response.data.reactions;
      })
      .catch(() => {
        this.errorMessage = this.$t('notFoundError');
      });
    },
  },
  beforeMount() {
    this.setup();
  },
};
</script>

<style lang="scss">

</style>
