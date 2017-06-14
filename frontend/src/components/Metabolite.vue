<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else class="metabolite-table">
    <table v-if="info && Object.keys(info).length != 0" id="main-table" class="table">
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
    <br>
    <table v-if="info && Object.keys(info).length != 0" id="hmdb-table" class="table">
      <tr v-for="(el, index) in HMDBRAbleKey">
        <td v-if="index === 0" :rowspan="Object.keys(info).length">HMDB</td>
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
    <reactome v-show="false"></reactome>
  </div>
</template>

<script>
import axios from 'axios';
import Reactome from 'components/Reactome';
import { chemicalFormula, chemicalName, chemicalNameLink } from '../helpers/chemical-formatters';


export default {
  name: 'metabolite',
  components: {
    Reactome,
  },
  data() {
    return {
      mId: this.$route.query.metabolite_rcid,
      mainTableKey: [
        { name: 'id', display: 'Identifier', modifier: this.reformatID },
        { name: 'long_name', display: 'Name' },
        { name: 'compartment' },
        { name: 'organism' },
        { name: 'formula', modifier: this.getChemicalFormula },
        { name: 'charge' },
        { name: 'mass', modifier: this.reformatMass },
        { name: 'kegg', modifier: this.reformatLink },
        { name: 'chebi' },
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
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.load();
    },
  },
  methods: {
    load() {
      axios.get(`metabolite/${this.mId}/`)
      .then((response) => {
        console.log(response.data);
        if (response.data.component_type === 'metabolite') {
          this.info = response.data;
        } else {
          this.errorMessage = this.$t('notFoundError');
        }
      })
      .catch((error) => {
        console.log('error:');
        console.log(error);
        this.errorMessage = this.$t('notFoundError');
      });
    },
    reformatID(id) {
      return id.slice(2);
    },
    reformatKey(k) {
      return `${k[0].toUpperCase()}${k.slice(1).replace('_', ' ')}`;
    },
    reformatLink(s) {
      return `<a href="${s}" target="_blank">${s}</a>`;
    },
    reformatMass(s) {
      return `${s} g/mol`;
    },
    getChemicalFormula(s) {
      return chemicalFormula(s);
    },
  },
  beforeMount() {
    this.load();
  },
  chemicalFormula,
  chemicalName,
  chemicalNameLink,
};
</script>

<style lang="scss">

#main-table tr td.td-key, #hmdb-table tr td.td-key {
  background: lightgray;
  width: 150px;
}

#hmdb-table tr:first-child > td:first-child {
  background: gray;
  color: white;
  width: 75px;
  vertical-align: middle;
}

</style>