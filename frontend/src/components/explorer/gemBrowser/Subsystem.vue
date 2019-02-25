<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else>
    <div class="columns">
      <div class="column">
        <h3 class="title is-3">Subsystem {{ !showLoader ? info.name : '' }}</h3>
      </div>
    </div>
    <loader v-show="showLoader"></loader>
    <div v-show="!showLoader" class="columns">
      <div class="subsystem-table column is-10">
        <table v-if="info && Object.keys(info).length != 0" class="table main-table is-fullwidth">
          <tr class="m-row" v-for="el in mainTableKey[model.database_name]" v-if="info[el.name]">
            <td v-if="el.display" class="td-key has-background-primary has-text-white-bis">{{ el.display }}</td>
            <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatKey(el.name) }}</td>
            <td v-if="info[el.name]">
              <span v-if="el.modifier" v-html="el.modifier(info[el.name])">
              </span>
              <span v-else>
                {{ info[el.name] }}
              </span>
            </td>
            <td v-else> - </td>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Compartments</td>
            <td>
              <template v-for="(c, i) in info['compartment']">
                <template v-if="i != 0">, </template>
                <router-link  :to="{ path: `/explore/gem-browser/${model.database_name}/compartment/${idfy(c)}` }"> {{ c }}</router-link>
              </template>
            </td>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Metabolites</td>
            <td>
              <div v-html="metabolitesListHtml"></div>
              <div v-if="!this.showFullMetabolite && this.metabolites.length > this.limitMetabolite">
                <br>
                <button class="is-small button" @click="showFullMetabolite=true">
                  ... and {{ this.metabolites.length - this.limitMetabolite}} more
                </button>
              </div>
            </td>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Enzymes</td>
            <td>
              <div v-html="enzymesListHtml"></div>
              <div v-if="!this.showFullEnzyme && this.enzymes.length > this.limitEnzyme">
                <br>
                <button class="is-small button" @click="showFullEnzyme=true">
                  ... and {{ this.enzymes.length - this.limitEnzyme}} more
                </button>
              </div>
            </td>
          </tr>
        </table>
        <h3 class="title is-3">Reactions</h3>
      </div>
      <div class="column">
        <div class="box has-text-centered">
          <div class="button is-info is-fullwidth" disabled>
            <p>View on {{ messages.mapViewerName }}</p>
          </div>
        </div>
      </div>
    </div>
    <div class="columns" v-show="!showLoader">
      <reaction-table :reactions="reactions" :showSubsystem="false" :model="model"></reaction-table>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Loader from 'components/Loader';
import ReactionTable from 'components/explorer/gemBrowser/ReactionTable';
import { reformatTableKey, idfy } from '../../../helpers/utils';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'subsystem',
  components: {
    ReactionTable,
    Loader,
  },
  props: ['model'],
  data() {
    return {
      messages,
      sName: this.$route.params.id,
      showLoader: false,
      info: {},
      metabolites: [],
      enzymes: [],
      reactions: [],
      errorMessage: '',
      mainTableKey: {
        hmr2: [
          { name: 'name', display: 'Name' },
          { name: 'system' },
        ],
      },
      showFullMetabolite: false,
      showFullEnzyme: false,
      limitMetabolite: 40,
      limitEnzyme: 40,
      idfy,
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.$route.path.includes('/subsystem/')) {
        if (this.sName !== this.$route.params.id) {
          this.setup();
        }
      }
    },
  },
  computed: {
    metabolitesListHtml() {
      const l = ['<span class="tags">'];
      this.metabolites.sort((a, b) => (a.name < b.name ? -1 : 1));
      let i = 0;
      for (const m of this.metabolites) {
        if (!this.showFullMetabolite && i === this.limitMetabolite) {
          break;
        }
        i += 1;
        l.push(`<span id="${m.id}" class="tag rcm"><a class="is-size-6">${m.full_name ? m.full_name : m.id}</a></span>`);
      }
      l.push('</span>');
      return l.join('');
    },
    enzymesListHtml() {
      const l = ['<span class="tags">'];
      this.enzymes.sort((a, b) => (a.name < b.name ? -1 : 1));
      let i = 0;
      for (const e of this.enzymes) {
        if (!this.showFullEnzyme && i === this.limitEnzyme) {
          break;
        }
        i += 1;
        l.push(`<span id="${e.id}" class="tag rce"><a class="is-size-6">${e.name ? e.name : e.id}</a></span>`);
      }
      l.push('</span>');
      return l.join('');
    },
  },
  methods: {
    setup() {
      this.sName = this.$route.params.id;
      this.load();
    },
    load() {
      this.showLoader = true;
      axios.get(`${this.model.database_name}/subsystem/${this.sName}/`)
      .then((response) => {
        this.info = response.data.subsystemAnnotations;
        this.metabolites = response.data.metabolites;
        this.enzymes = response.data.enzymes;
        this.reactions = response.data.reactions;
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
