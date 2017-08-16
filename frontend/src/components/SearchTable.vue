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
    <div>
      <div class="tabs is-boxed is-fullwidth">
        <ul>
          <li :disabled="resultsCount[tab] === 0" 
          :class="[{'is-active': showTab(tab) && resultsCount[tab] !== 0 }, { 'is-disabled': resultsCount[tab] === 0 }]" 
          v-for="tab in tabs" @click="resultsCount[tab] !== 0 ? showTabType=tab : ''">
            <a>{{ tab | capitalize }} ({{ resultsCount[tab] }})</a>
          </li>
        </ul>
      </div>
      <div v-show="showTab('metabolite') && resultsCount['metabolite'] !== 0">
        <div class="button" 
        v-on:click="toggleFilter('metabolite')" 
        :disabled="disabledFilters['metabolite']"
        :class="{'is-active': toggleFilters['metabolite'], 'is-primary': Object.keys(activeFilters['metabolite']).length !== 0}"
        >Filters</div>
        <div class="box columns" v-show="toggleFilters['metabolite']">
          <div class="column" v-for="(types, key) in filters['metabolite']">
            {{ key | capitalize }}
            <select :disabled="types.length === 1"
            @change="doFilterResults('metabolite', key, $event)">
              <option v-for="el in types">
                {{ el }}
              </option>
            </select>
          </div>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>Organism</th><th>Model</th><th>Subsystem</th><th>Compartment</th>
              <th>ID</th><th>Name</th><th>Formula</th><th>HMDB ID</th><th>Link</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in searchResultsSplittedFiltered['metabolite']">
              <td>{{ item.organism | capitalize }}</td>
              <td>the model</td>
              <td>the pathway</td>
              <td>{{ item.compartment | capitalize }}</td>
              <td>{{ item.id.slice(2) }}</td>
              <td>{{ item.short_name }}</td>
              <td v-html="formulaFormater(item.formula)"></td>
              <td>{{ item.metabolite ? item.metabolite.hmdb : '' }}</td>
              <td>link</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-show="showTab('enzyme') && resultsCount['enzyme'] !== 0">
        Enzyme results
        <div class="columns">
          <div class="column">
            <table class="table">
              <thead>
                <tr>
                  <th>Organism</th><th>Model</th><th>Subsystem</th><th>Compartment</th><th>ID</th>
                  <th>Name</th><th>Formula</th><th>Uniprot ID</th><th>Link</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in searchResultsSplitted['enzyme']">
                  <td>{{ item.organism | capitalize }}</td>
                  <td>the model</td>
                  <td>the pathway</td>
                  <td>{{ item.compartment | capitalize }}</td>
                  <td>{{ item.id.slice(2) }}</td>
                  <td>{{ item.short_name }}</td>
                  <td v-html="formulaFormater(item.formula)"></td>
                  <td>{{ item.enzyme ? item.enzyme.uniprot_acc : '' }}</td>
                  <td>link</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div v-show="showTab('reaction') && resultsCount['reaction'] !== 0">
        Reaction results
        <div class="columns">
          <div class="column">
            <table class="table">
              <thead>
                <tr>
                  <th>Organism</th><th>Model</th><th>Subsystem</th><th>Compartment</th>
                  <th>ID</th><th>Equation</th><th>Link</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in searchResultsSplitted['reaction']">
                  <td>{{ item.organism | capitalize }}</td>
                  <td>the model</td>
                  <td>the pathway</td>
                  <td>{{ item.compartment | capitalize }}</td>
                  <td>{{ item.id }}</td>
                  <td>{{ item.equation }}</td>
                  <td>link</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div v-show="showTab('subsystem') && resultsCount['subsystem'] !== 0">
        Pathway results
        <div class="columns">
          <div class="column">
            <table class="table">
              <thead>
                <tr>
                  <th>Organism</th><th>Model</th><th>Pathway</th><th>Compartment</th>
                  <th>Link</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in searchResultsSplitted['subsystem']">
                  <td>{{ item.organism | capitalize }}</td>
                  <td>the model</td>
                  <td>the subsystem</td>
                  <td>{{ item.compartment | capitalize }}</td>
                  <td>link</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div v-show="showTab('compartment') && resultsCount['compartment'] !== 0">
        Compartement results
        <div class="columns">
          <div class="column">
            <table class="table">
              <thead>
                <tr>
                  <th>Organism</th><th>Model</th><th>Compartment</th><th>Link</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in searchResultsSplitted['compartment']">
                  <td>{{ item.organism | capitalize }}</td>
                  <td>the model</td>
                  <td>{{ item.compartment | capitalize }}</td>
                  <td>link</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      </div>
      <div v-show="!showTabType">
        <div v-if="searchResults.length === 0" class="column is-8 is-offset-2 has-text-centered">
          {{ $t('searchNoResult') }}
        </div>
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
      selectedFilter: '',
      toggleFilters: {
        metabolite: false,
      },
      activeFilters: {},
      disabledFilters: {},

      tabs: [
        'metabolite',
        'enzyme',
        'reaction',
        'subsystem',
        'compartment',
      ],
      resultsCount: {},
      filters: {
        metabolite: {
          organism: {},
          model: {},
          compartment: {},
          subsystem: {},
        },
        enzyme: {
          organism: {},
          model: {},
          compartment: {},
          subsystem: {},
        },
        reaction: {
          organism: {},
          model: {},
          compartment: {},
          subsystem: {},
        },
        subsystem: {
          organism: {},
          model: {},
          compartment: {},
        },
        compartment: {
          organism: {},
          model: {},
        },
      },
      searchTerm: 'metabolite',
      searchResults: [],
      showTabType: '',
    };
  },
  computed: {
    searchResultsOrdered() {
      // copy to avoid to mutate the origin array (watched)
      let res = Array.prototype.slice.call(this.searchResults);
      res = res.sort(compare('component_type', 'asc'));
      return res;
    },
    searchResultsSplitted() {
      return this.searchResultsOrdered.reduce((subarray, el) => {
        const arr = subarray;
        if (!arr[el.component_type]) { arr[el.component_type] = []; }
        arr[el.component_type].push(el);
        return arr;
      }, {});
    },
    searchResultsSplittedFiltered() {
      const arr = JSON.parse(JSON.stringify(this.searchResultsSplitted));
      for (const key of Object.keys(this.activeFilters)) {
        for (const compo of Object.keys(this.activeFilters[key])) {
          const val = this.activeFilters[key][compo];
          arr[key] = arr[key].filter(el => el[compo].toLowerCase() === val.toLowerCase());
        }
      }
      return arr;
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
    toggleFilter(type) {
      if (this.disabledFilters[type]) {
        this.toggleFilters[type] = false;
        return;
      }
      this.toggleFilters[type] = !this.toggleFilters[type];
    },
    countResults() {
      for (const key of this.tabs) {
        this.resultsCount[key] = 0;
      }
      for (const el of this.searchResults) {
        if (el.component_type in this.resultsCount) {
          this.resultsCount[el.component_type] += 1;
        } else {
          this.resultsCount.metabolite += 1;
        }
      }
    },
    fillFilterFields() {
      // get the otion values of the <select> in the filter panels
      // reset filter
      for (const type of Object.keys(this.filters)) {
        for (const field of Object.keys(this.filters[type])) {
          this.filters[type][field] = {};
        }
      }

      // store choice only once in a dict
      for (const el of this.searchResults) {
        const componentType = el.component_type;
        for (const field of Object.keys(this.filters[componentType])) {
          this.filters[componentType][field][el[field]] = 1;
        }
      }

      // convert dict in array ad add 'None' if more than one choice
      for (const kType of Object.keys(this.filters)) {
        let validFilter = false;
        const fields = this.filters[kType];
        for (const kComp of Object.keys(fields)) {
          // console.log(`kComp ${kComp}`);
          const values = fields[kComp];
          if (Object.keys(values).length === 1) {
            this.filters[kType][kComp] = Object.keys(values);
          } else {
            this.filters[kType][kComp] = ['None'].concat(Object.keys(values).sort());
            validFilter = true;
          }
        }
        if (!validFilter) {
          // of all filter contains only one choice
          // desactivate the filter panel
          this.disabledFilters[kType] = true;
          this.toggleFilters[kType] = false;
        }
      }
    },
    updateResults(term, val) {
      this.searchTerm = term;
      this.searchResults = val;
      // count types
      this.countResults();
      // get filters
      this.fillFilterFields();
      // select the active tab
      for (const key of Object.keys(this.resultsCount)) {
        if (this.resultsCount[key] !== 0) {
          this.showTabType = key;
          return;
        }
      }
      this.showTabType = '';
    },
    doFilterResults(type, compo, event) {
      const select = event.srcElement;
      const value = select.options[select.selectedIndex].innerHTML.trim().toLowerCase();

      // copy the dict of filter to trigger the change
      const test = JSON.parse(JSON.stringify(this.activeFilters));
      if (value === 'none') {
        delete test[type][compo];
      } else {
        test[type][compo] = value;
      }
      // trigger changes in the computed property 'searchResultsSplittedFiltered'
      this.activeFilters = test;
    },
    showTab(elementType) {
      return this.showTabType === elementType;
    },
  },
  created() {
    // init filter booleans
    for (const tabname of this.tabs) {
      this.toggleFilters[tabname] = false;
      this.activeFilters[tabname] = {};
      this.disabledFilters[tabname] = false;
    }
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

.tabs li.is-disabled {
  cursor: not-allowed;
  color: gray;
  opacity: 0.75;

  a {
    cursor: not-allowed;
  }
}

</style>
