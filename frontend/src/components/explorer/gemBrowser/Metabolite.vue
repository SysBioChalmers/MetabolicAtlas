<template>
  <div id="metabolite-page">
    <div v-if="errorMessage" class="columns">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </div>
    <div v-else>
      <div class="columns">
        <div class="column">
          <h3 class="title is-3">Metabolite</h3>
        </div>
      </div>
      <div class="columns metabolite-table">
        <div class="column is-10">
          <div id="metabolite-table">
            <table v-if="info && Object.keys(info).length != 0" class="table main-table is-fullwidth">
              <tr v-for="el in mainTableKey[model]">
                <td v-if="el.display" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
                <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                <td v-if="info[el.name] !== null">
                  <span v-if="el.modifier" v-html="el.modifier(info[el.name])">
                  </span>
                  <span v-else>
                    {{ info[el.name] }}
                  </span>
                </td>
                <td v-else> - </td>
              </tr>
            </table>
            <template v-if="hasExternalID">
              <br>
              <span class="subtitle">External IDs</span>
              <table v-if="info && Object.keys(info).length != 0" id="ed-table" class="table is-fullwidth">
                <tr v-for="el in externalIDTableKey[model]" v-if="info[el.name] && info[el.link]">
                  <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
                  <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                  <td>
                    <span v-html="reformatLink(info[el.name], info[el.link])">
                    </span>
                  </td>
                </tr>
              </table>
            </template>
          </div>
        </div>
        <div class="column">
          <div class="box has-text-centered">
            <div class="button is-info" disabled>
              <p>View on Map Viewer</p>
            </div>
            <br><br>
            <div class="button is-info"
              @click="viewInteractionPartners">
              View interaction partners
            </div>
          </div>
        </div>
      </div> 
      <div class="columns">
        <reactome v-show="showReactome" id="metabolite-reactome" :model="this.model" :metaboliteID="metaboliteID"></reactome>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Reactome from 'components/explorer/gemBrowser/Reactome';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../../../helpers/chemical-formatters';
import { reformatTableKey, reformatStringToLink, addMassUnit } from '../../../helpers/utils';

export default {
  name: 'metabolite',
  components: {
    Reactome,
  },
  props: ['model'],
  data() {
    return {
      mId: this.$route.params.id,
      metaboliteID: '',
      mainTableKey: {
        hmr2: [
          { name: 'name' },
          { name: 'alt_name', display: 'alternate name' },
          { name: 'aliases', display: 'Synonyms' },
          { name: 'description', display: 'Description' },
          { name: 'formula', modifier: chemicalFormula },
          { name: 'charge' },
          { name: 'inchi' },
          { name: 'compartment' },
          { name: 'id', display: 'Model&nbsp;ID' },
        ],
        yeast: [
          { name: 'name' },
          { name: 'alt_name', display: 'alternate name' },
          { name: 'aliases', display: 'Synonyms' },
          { name: 'description', display: 'Description' },
          { name: 'formula', modifier: chemicalFormula },
          { name: 'charge' },
          { name: 'inchi' },
          { name: 'compartment' },
          { name: 'id', display: 'Model&nbsp;ID' },
        ],
      },
      externalIDTableKey: {
        hmr2: [
          { name: 'hmdb_id', display: 'HMDB ID', link: 'hmdb_link' },
          { name: 'chebi_id', display: 'Chebi ID', link: 'chebi_link' },
          { name: 'mnxref_id', display: 'Mnxref ID', link: 'mnxref_link' },
        ],
        yeast: [
        ],
      },
      info: {},
      errorMessage: '',
      activePanel: 'table',
      showReactome: false,
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.$route.path.includes('/metabolite/')) {
        if (this.mId !== this.$route.params.id) {
          this.setup();
        }
      }
    },
  },
  computed: {
    hasExternalID() {
      for (const item of this.externalIDTableKey[this.model]) {
        if (this.info[item.name] && this.info[item.link]) {
          return true;
        }
      }
      return false;
    },
  },
  methods: {
    setup() {
      this.mId = this.$route.params.id;
      if (this.mId) {
        this.load();
      }
    },
    load() {
      axios.get(`${this.model}/metabolites/${this.mId}/`)
      .then((response) => {
        this.metaboliteID = this.mId;
        this.info = response.data;
        this.showReactome = true;
      })
      .catch(() => {
        this.errorMessage = this.$t('notFoundError');
        this.showReactome = false;
      });
    },
    reformatTableKey(k) { return reformatTableKey(k); },
    reformatLink(s, link) { return reformatStringToLink(s, link); },
    reformatMass(s) { return addMassUnit(s); },
    viewInteractionPartners() {
      this.$router.push(`/explore/gem-browser/${this.model}/interaction/${this.mId}`);
    },
  },
  beforeMount() {
    this.setup();
  },
  chemicalFormula,
  chemicalName,
  chemicalNameExternalLink,
};
</script>

<style lang="scss">

.metabolite-table, .model-table, .reaction-table, .subsystem-table {
  .main-table tr td.td-key, #ed-table tr td.td-key {
    width: 150px;
  }
}

</style>