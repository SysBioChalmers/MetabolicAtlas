<template>
  <div>
  <div class="container columns">
    <div class="column is-offset-3">
      <global-search
      :quickSearch=false
      :searchTerm=searchTerm
      @updateResults="updateResults">

      </global-search>
      searchterm = {{ searchTerm }}
      result = {{ searchResults.length }}
    </div>
  </div>
  <div class="columns">
    <div v-if="searchResults.length === 0" class="column is-8 is-offset-2 has-text-centered">
      {{ $t('noResultFound') }}
    </div>
    <div v-else class="column">
      <table>
        <tr v-for="item in searchResultsOrdered">
          <td>
            <table>
            <tr>
              <td class="lab">ID</td>
              <td>{{ item.id }}</td>
              <td class="lab">Compartment</td>
              <td>{{ item.compartment }}</td>
              <td class="lab">uniprot ACC</td>
              <td>item.</td>
              <td rowspan="4">
                linkA<br>
                linkB
              </td>
            </tr>
            <tr>
              <td class="lab">Name</td>
              <td>{{ item.short_name }}</td>
              <td class="lab">Organism</td>
              <td>{{ item.organism }}</td>
              <td class="lab">other ACC</td>
              <td>otherID</td>
            </tr>
            <tr>
              <td class="lab">Full name</td>
              <td>{{ item.long_name }}</td>
              <td class="lab">Formula</td>
              <td>{{ item.formula }}</td>
              <td class="lab">Kegg</td>
              <td>-</td>
            </tr>
            <tr>
              <td class="lab">Type</td>
              <td v-bind:class="item.component_type === 'enzyme' ? 'red' : 'green'">{{ item.component_type }}</td>
              <td class="lab">Mass</td>
              <td>132.45</td>
              <td></td>
              <td></td>
            </tr>
            </table>
            {{ item }}
          </td>
        </tr>
      </table>
    </div>
  </div>
  </div>
</template>

<script>
import GlobalSearch from 'components/GlobalSearch';
import { default as compare } from '../helpers/compare';

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
  methods: {
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
};

</script>

<style lang="scss">

.red {
  color: #ffadad;
}

.green {
  color: #bbff99;
}

td {
  table {
    border-collapse: collapse;
    border: 1px solid black;

    td {
      padding-left: 5px;
      padding-right: 5px;
    }

    tr:first-child > td:last-child {
      border-left: 1px solid black;
    }
  }

}


table td.lab {
  font-weight: 600;
  background: lightgray;
  width: 150px;
  border: 1px solid gray;
}

</style>
