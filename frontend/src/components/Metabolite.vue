<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else class="metabolite-table">
    <table v-if="info && Object.keys(info).length != 0" class="table main-table">
      <tr v-for="el in mainTableKey">
        <td v-if="el.display" class="td-key">{{ el.display }}</td>
        <td v-else class="td-key">{{ reformatKey(el.name) }}</td>
        <td v-if="info.metabolite[el.name]">
          <span v-if="el.modifier" v-html="el.modifier(info.metabolite[el.name])">
          </span>
          <span v-else>
            {{ info.metabolite[el.name] }}
          </span>
        </td>
        <td v-else-if="info[el.name]">
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
      <table v-if="info && Object.keys(info).length != 0" id="hmdb-table" class="table">
        <tr v-for="el in HMDBRAbleKey">
          <td v-if="el.display" class="td-key">{{ el.display }}</td>
          <td v-else class="td-key">{{ reformatKey(el.name) }}</td>
          <td v-if="info.metabolite[el.name]">
            <span v-if="el.modifier" v-html="el.modifier(info.metabolite[el.name])">
            </span>
            <span v-else>
              {{ info.metabolite[el.name] }}
            </span>
          </td>
          <td v-else-if="info[el.name]">
            <span v-if="el.modifier" v-html="el.modifier(info[el.name])">
            </span>
            <span v-else>
              {{ info[el.name] }}
            </span>
          </td>
          <td v-else> - </td>
        </tr>
      </table>
    </div>
    <reactome></reactome>
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
  data() {
    return {
      mId: this.$route.query.id,
      mainTableKey: [
        { name: 'id', display: 'Identifier' },
        { name: 'long_name', display: 'Name' },
        { name: 'compartment' },
        { name: 'organism' },
        { name: 'formula', modifier: chemicalFormula },
        { name: 'charge' },
        { name: 'mass', modifier: this.reformatMass },
        { name: 'kegg', modifier: this.reformatKeggLink },
        { name: 'chebi', modifier: this.reformatChebiLink },
        { name: 'inchi' },
        { name: 'pubchem_link', modifier: this.reformatLink },
      ],
      HMDBRAbleKey: [
        { name: 'hmdb_description', display: 'Description' },
        { name: 'hmdb_function', display: 'Function' },
        { name: 'hmdb_link', display: 'Link', modifier: this.reformatLink },
      ],
      info: {},
      errorMessage: '',
      showHMDB: false,
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
      this.mId = this.$route.query.id;
      this.load();
    },
    load() {
      axios.get(`metabolite/${this.mId}/`)
      .then((response) => {
        if (response.data.component_type === 'metabolite' &&
          response.data.metabolite) {
          this.info = response.data;
          this.showHMDB = this.hasHMDBInfo();
        } else {
          this.errorMessage = this.$t('notFoundError');
        }
      })
      .catch(() => {
        this.errorMessage = this.$t('notFoundError');
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
      for (const key of ['hmdb_description', 'hmdb_function', 'hmdb_link']) {
        if (this.info.metabolite[key]) {
          return true;
        }
      }
      return false;
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

.metabolite-table, .model-table, .reaction-table {
  .main-table tr td.td-key, #hmdb-table tr td.td-key {
    background: #64CC9A;
    width: 150px;
    color: white;
  }
}

</style>