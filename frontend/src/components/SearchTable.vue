<template>
  <div>
  <div class="container columns">
    <div class="column is-offset-3">
      <global-search
      :quickSearch=false
      :searchTerm=searchTerm
      @updateResults="updateResults">
      </global-search>
    </div>
  </div>
  <div class="columns">
    <div v-if="searchResults.length === 0" class="column is-8 is-offset-2 has-text-centered">
      {{ $t('searchNoResult') }}
    </div>
    <div v-else class="column">
      Results: {{ searchResults.length }}
      <table class="table main">
        <thead>
          <tr>
            <th>Organism</th>
            <th>Type</th>
            <th>Compartment</th>
            <th>ID</th>
            <th>Name</th>
            <th>Formula</th>
            <th>HMDB/Uniprot ID</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in searchResultsOrdered">
            <td>{{ item.organism | capitalize }}</td>
            <td v-bind:class="item.component_type === 'enzyme' ? 'red' : 'green'">{{ item.component_type | capitalize }}</td>
            <td>{{ item.compartment | capitalize }}</td>
            <td>{{ item.id.slice(2) }}</td>
            <td>{{ item.short_name }}</td>
            <td v-html="formulaFormater(item.formula)"></td>
            <td v-if="item.enzyme || item.metabolite">{{ item.component_type === 'enzyme' ? item.enzyme.uniprot_acc : item.metabolite.hmdb }}</td>
            <td v-else></td>
            <td></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  </div>
</template>

<script>
import GlobalSearch from 'components/GlobalSearch';
import { default as compare } from '../helpers/compare';
import { chemicalFormula } from '../helpers/chemical-formatters';

export default {
  name: 'search-table',
  components: {
    GlobalSearch,
  },
  data() {
    return {
      searchTerm: '',
      searchResults: [],
    };
  },
  computed: {
    searchResultsOrdered() {
      let res = this.searchResults;
      res = res.sort(compare('component_type', 'asc'));
      return res;
    },
  },
  filters: {
    capitalize(value) {
      if (!value) {
        return '';
      }
      return value.charAt(0).toUpperCase() + value.slice(1);
    },
  },
  methods: {
    formulaFormater(s) {
      return chemicalFormula(s);
    },
    updateResults(term, val) {
      this.searchTerm = term;
      this.searchResults = val;
    },
  },
  beforeMount() {
    this.searchTerm = this.$route.query.term;
  },
  mounted() {
    if (this.searchTerm) {
      // trigger the search in child component
      this.$children[0].search(this.searchTerm);
    }
  },
  chemicalFormula,
};

</script>

<style lang="scss">

.red {
  color: #ff1a1a;
}

.green {
  color: #33cc33;
}

table.main

table td.lab {
  font-weight: 600;
  background: lightgray;
  width: 150px;
  border: 1px solid gray;
}

</style>
