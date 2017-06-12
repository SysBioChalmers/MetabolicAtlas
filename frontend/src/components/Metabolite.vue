<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else class="metabolite-table">
    <table v-if="info && Object.keys(info).length != 0" class="table">
      <tr v-for="el in tableKeyOrder">
        <td v-if="el.display">{{ el.display }}</td>
        <td v-else>{{ reformatKey(el.name) }}</td>
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
</template>

<script>
import axios from 'axios';
import { chemicalFormula, chemicalName, chemicalNameLink } from '../helpers/chemical-formatters';

export default {
  name: 'metabolite',
  data() {
    return {
      mId: this.$route.query.id,
      tableKeyOrder: [
        { name: 'id', display: 'Metabolic Atlas ID', modifier: this.reformatID },
        { name: 'long_name', display: 'Name' },
        { name: 'compartment' },
        { name: 'organism' },
        { name: 'formula', modifier: this.getChemicalFormula },
        { name: 'mass' },
        { name: 'hmdb_description', display: 'HMDB description' },
        { name: 'hmdb_link', modifier: this.reformatLink },
        { name: 'kegg', modifier: this.reformatLink },
        { name: 'pubchem_link', modifier: this.reformatLink },
      ],
      info: {},
      errorMessage: '',
    };
  },
  methods: {
    load() {
      axios.get(`metabolite/${this.mId}/`)
      .then((response) => {
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
      return `<a :href="${s}" target="_blank">${s}</a>`;
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

.metabolite-table tr > td:first-child {
  background: lightgray;
  width: 150px;
}

</style>