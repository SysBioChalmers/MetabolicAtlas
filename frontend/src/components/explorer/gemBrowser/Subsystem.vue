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
    <div v-show="!showLoader" class="columns is-multiline is-variable is-8">
      <div class="subsystem-table column is-10-widescreen is-9-desktop is-full-tablet">
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
                <template v-if="i !== 0">, </template>
                <router-link  :to="{ path: `/explore/gem-browser/${model.database_name}/compartment/${idfy(c)}` }"> {{ c }}</router-link>
              </template>
            </td>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Metabolites</td>
            <td>
              <div v-html="metabolitesListHtml"></div>
              <div v-if="!this.showFullMetabolite && this.metabolites.length > this.displayedMetabolite">
                <br>
                <button class="is-small button" @click="showFullMetabolite=true">
                  ... and {{ this.metabolites.length - this.displayedMetabolite}} more
                </button>
                <span v-show="this.metabolites.length == this.limitMetabolite" class="tag is-medium is-warning is-pulled-right">
                  The number of metabolites displayed is limited to {{ this.limitMetabolite }}.
                </span>
              </div>
            </td>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">Enzymes</td>
            <td>
              <div v-html="enzymesListHtml"></div>
              <div v-if="!this.showFullEnzyme && this.enzymes.length > this.displayedEnzyme">
                <br>
                <button class="is-small button" @click="showFullEnzyme=true">
                  ... and {{ this.enzymes.length - this.displayedEnzyme}} more
                </button>
                <span v-show="this.enzymes.length == this.limitEnzyme" class="tag is-medium is-warning is-pulled-right">
                  The number of enzymes displayed is limited to {{ this.limitEnzyme }}.
                </span>
              </div>
            </td>
          </tr>
        </table>
      </div>
      <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
        <maps-available :model="this.model" :type="'subsystem'" :id="this.sName" :elementID="''"></maps-available>
      </div>
    </div>
    <template v-if="!this.showLoader">
      <h4 class="title is-4">Reactions</h4>
    </template>
    <div class="columns">
      <div class="column">
        <template v-if="!this.showLoader && this.showReactionLoader">
          <loader></loader>
        </template>
        <template v-else-if="!this.showReactionLoader">
          <reaction-table :reactions="this.reactions" :showSubsystem="false" :model="this.model" :limit="this.limitReaction"></reaction-table>
        </template>
      </div>
    </div>
  </div>
</template>


<script>
import axios from 'axios';
import Loader from 'components/Loader';
import MapsAvailable from 'components/explorer/gemBrowser/MapsAvailable';
import ReactionTable from 'components/explorer/gemBrowser/ReactionTable';
import { reformatTableKey, idfy } from '../../../helpers/utils';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'subsystem',
  components: {
    MapsAvailable,
    ReactionTable,
    Loader,
  },
  props: ['model'],
  data() {
    return {
      messages,
      sName: this.$route.params.id,
      showLoader: true,
      showReactionLoader: true,
      info: {},
      metabolites: [],
      enzymes: [],
      reactions: [],
      errorMessage: '',
      mainTableKey: {
        hmr2: [
          { name: 'name', display: 'Name' },
        ],
      },
      showFullMetabolite: false,
      showFullEnzyme: false,
      displayedMetabolite: 40,
      displayedEnzyme: 40,
      limitMetabolite: 0,
      limitEnzyme: 0,
      limitReaction: 0,
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
      console.log(this.showFullMetabolite, this.limitMetabolite);
      const l = ['<span class="tags">'];
      this.metabolites.sort((a, b) => (a.name < b.name ? -1 : 1));
      let i = 0;
      for (const m of this.metabolites) {
        if ((!this.showFullMetabolite && i === this.displayedMetabolite) ||
          i === this.limitMetabolite) {
          console.log('break');
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
        if ((!this.showFullEnzyme && i === this.displayedEnzyme) ||
          i === this.limitEnzyme) {
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
      this.getReactions();
    },
    load() {
      this.showLoader = true;
      axios.get(`${this.model.database_name}/subsystem/${this.sName}/summary/`)
      .then((response) => {
        this.info = response.data.info;
        this.metabolites = response.data.metabolites;
        this.enzymes = response.data.enzymes;
        this.limitMetabolite = response.data.limit;
        this.limitEnzyme = response.data.limit;
        this.showLoader = false;
      })
      .catch(() => {
        this.errorMessage = messages.notFoundError;
      });
    },
    getReactions() {
      this.showReactionLoader = true;
      axios.get(`${this.model.database_name}/subsystem/${this.sName}/reaction_list`)
      .then((response) => {
        this.reactions = response.data.reactions;
        this.limitReaction = response.data.limit;
        this.showReactionLoader = false;
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
