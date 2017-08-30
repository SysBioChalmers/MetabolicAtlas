<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else class="reaction-table">
    <table v-if="info && Object.keys(info).length != 0" id="main-table" class="table">
      <tr v-for="el in mainTableKey">
        <td v-if="el.display" class="td-key">{{ el.display }}</td>
        <td v-else class="td-key">{{ reformatKey(el.name) }}</td>
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
  </div>
</template>

<script>
import axios from 'axios';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../helpers/chemical-formatters';

export default {
  name: 'reaction',
  data() {
    return {
      rId: this.$route.query.reaction_component_id,
      mainTableKey: [
        { name: 'id', display: 'Identifier' },
        { name: 'name', display: 'Name', modifier: chemicalName },
        { name: 'compartment' },
        { name: 'subsystem', modifier: this.reformatList },
        { name: 'equation', modifier: chemicalFormula },
        { name: 'lower_bound' },
        { name: 'upper_bound' },
        { name: 'objective_coefficient', modifier: this.reformatMass },
        { name: 'reactants', modifier: this.reformatCount },
        { name: 'products', modifier: this.reformatCount },
        { name: 'Ec', display: 'EC', modifier: this.reformatLink },
        { name: 'sbo_id', display: 'SBO ID', modifier: this.reformatLink },
      ],
      info: {},
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
      this.rId = this.$route.query.reaction_component_id;
      this.load();
    },
    load() {
      axios.get(`reactions/${this.rId}/`)
      .then((response) => {
        this.info = response.data;
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
    reformatLink(s, link) {
      if (link) {
        return `<a href="${link}" target="_blank">${s}</a>`;
      }
      return `<a href="${s}" target="_blank">${s}</a>`;
    },
    reformatMass(s) {
      return `${s} g/mol`;
    },
    reformatList(l) {
      return l.join('; ');
    },
    reformatCount(e) {
      return e.length;
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

.metabolite-table {
  #main-table tr td.td-key {
    background: #64CC9A;
    width: 150px;
    color: white;
  }
}

</style>