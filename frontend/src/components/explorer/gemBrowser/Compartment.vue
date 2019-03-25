<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else>
    <div class="columns">
      <div class="column">
        <h3 class="title is-3">Compartment {{ compartment.name }}</h3>
      </div>
    </div>
    <loader v-show="showLoader"></loader>
    <div v-show="!showLoader" class="columns is-multiline is-variable is-8">
      <div class="subsystem-table column is-10-widescreen is-9-desktop is-full-tablet">
        <table v-if="compartment && Object.keys(compartment).length != 0" class="table main-table is-fullwidth">
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Name</td>
            <td> {{ this.compartment.name }}</td>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Subsystems</td>
             <td>
              <div v-html="subsystemListHtml"></div>
              <div v-if="!this.showFullSubsystem && this.subsystems.length > this.limitSubsystem">
                <br>
                <button class="is-small button" @click="showFullSubsystem=true">
                  ... and {{ this.subsystems.length - this.limitSubsystem}} more
                </button>
              </div>
            </td>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Reactions</td>
            <td> {{ this.compartment.reaction_count }}</td>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Metabolites</td>
            <td> {{ this.compartment.metabolite_count }}</td>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Enzymes</td>
            <td> {{ this.compartment.enzyme_count }}</td>
          </tr>
        </table>
        <span class="is-size-5">The <a :href="`/api/${model.database_name}/compartment/${this.cName}/`" target="_blank">complete list in JSON format</a> of reactions / metabolites / enzymes is available using our <a href="/swagger" target="_blank">API</a></span>
      </div>
      <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
        <router-link class="button is-info is-fullwidth is-outlined"
          :to="{ path: `/explore/map-viewer/${model.database_name}/compartment/${this.cName == 'cytosol' ? 'cytosol_1' : this.cName}?dim=2d` }">
          <span class="icon is-large"><i class="fa fa-map-o"></i></span>
          <span>{{ messages.mapViewerName }}</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Loader from 'components/Loader';
import { reformatTableKey } from '../../../helpers/utils';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'subsystem',
  components: {
    Loader,
  },
  props: ['model'],
  data() {
    return {
      messages,
      cName: this.$route.params.id,
      showLoader: false,
      compartment: {},
      subsystems: [],
      errorMessage: '',
      showFullSubsystem: false,
      limitSubsystem: 30,
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.$route.path.includes('/compartment/')) {
        if (this.cName !== this.$route.params.id) {
          this.setup();
        }
      }
    },
  },
  computed: {
    subsystemListHtml() {
      const l = ['<span class="tags">'];
      this.subsystems.sort((a, b) => (a < b ? -1 : 1));
      let i = 0;
      for (const s of this.subsystems) {
        if (!this.showFullSubsystem && i === this.limitSubsystem) {
          break;
        }
        i += 1;
        l.push(`<span id="${s}" class="tag sub"><a class="is-size-6">${s}</a></span>`);
      }
      l.push('</span>');
      return l.join('');
    },
  },
  methods: {
    setup() {
      this.cName = this.$route.params.id;
      this.load();
    },
    load() {
      this.showLoader = true;
      axios.get(`${this.model.database_name}/compartment/${this.cName}/stats/`)
      .then((response) => {
        this.compartment = response.data.compartmentAnnotations;
        this.subsystems = response.data.subsystems;
        this.showLoader = false;
      })
      .catch(() => {
        this.errorMessage = messages.notFoundError;
      });
    },
    reformatKey(k) { return reformatTableKey(k); },
  },
  beforeMount() {
    this.setup();
  },
};
</script>

<style lang="scss">
</style>
