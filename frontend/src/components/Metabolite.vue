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
          <p id="met-title" class="title is-1">Metabolite</p>
        </div>
      </div>
      <div class="columns metabolite-table">
        <div class="column is-10">
          <div id="metabolite-table">
            <table v-if="info && Object.keys(info).length != 0" class="table main-table is-fullwidth">
              <tr v-for="el in mainTableKey[model]">
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
            </table>
            <div v-show="showHMDB">
              <br>
              <span class="subtitle">HMDB</span>
              <table v-if="info && Object.keys(info).length != 0" id="hmdb-table" class="table is-fullwidth">
                <tr v-for="el in HMDBRAbleKey">
                  <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis">{{ el.display }}</td>
                  <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatKey(el.name) }}</td>
                  <td v-if="info[el.name]">
                    <span v-if="'modifier' in el" v-html="el.modifier(info[el.name])">
                    </span>
                    <span v-else>
                      {{ info[el.name] }}
                    </span>
                  </td>
                  <td v-else> - </td>
                </tr>
              </table>
            </div>
          </div>
        </div>
        <div class="column">
          <div class="box has-text-centered">
            <div class="button is-info">
              <p><i class="fa fa-eye"></i> on Metabolic Viewer<p>
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
import Reactome from 'components/Reactome';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../helpers/chemical-formatters';


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
          { name: 'formula', modifier: chemicalFormula },
          { name: 'charge' },
          { name: 'inchi' },
          { name: 'compartment' },
          { name: 'id', display: 'Model ID' },
          { name: 'kegg', modifier: this.reformatKeggLink },
          { name: 'chebi', modifier: this.reformatChebiLink },
          { name: 'pubchem_link', display: 'Pubchem', modifier: this.reformatLink },
        ],
      },
      HMDBRAbleKey: [
        { name: 'description', display: 'Description' },
        { name: 'function', display: 'Function' },
        { name: 'hmdb_link', display: 'Link', modifier: this.reformatLink },
      ],
      info: {},
      errorMessage: '',
      activePanel: 'table',
      showHMDB: false,
      showReactome: false,
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
        this.showHMDB = this.hasHMDBInfo();
        this.showReactome = true;
      })
      .catch((error) => {
        console.log(error);
        this.errorMessage = this.$t('notFoundError');
        this.showReactome = false;
      });
    },
    reformatID(id) {
      return id.slice(2);
    },
    reformatKey(k) {
      return `${k[0].toUpperCase()}${k.slice(1).replace('_', ' ')}`;
    },
    reformatKeggLink(s) {
      return `<a href="http://www.genome.jp/dbget-bin/www_bget?${s}" target="_blank">${s}</a>`;
    },
    reformatChebiLink(s) {
      return `<a href="http://www.ebi.ac.uk/chebi/searchId.do?chebiId=${s}" target="_blank">${s}</a>`;
    },
    reformatLink(s) {
      return `<a href="${s}" target="_blank">${s}</a>`;
    },
    reformatMass(s) {
      return `${s} g/mol`;
    },
    hasHMDBInfo() {
      for (const key of ['hmdb_id']) {
        if (this.info[key]) {
          return true;
        }
      }
      return false;
    },
    viewInteractionPartners() {
      this.$router.push(`/GemsExplorer/${this.model}/interaction/${this.mId}`);
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

 #met-title {
  padding-bottom: 2rem;
 }

.metabolite-table, .model-table, .reaction-table, .subsystem-table {
  .main-table tr td.td-key, #hmdb-table tr td.td-key {
    width: 150px;
  }
}

</style>