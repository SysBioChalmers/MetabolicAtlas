<template>
  <div id="search-table">
    <div class="container columns">
      <div class="column is-offset-3">
        <global-search
        :quickSearch=false
        :searchTerm=searchTerm
        @updateResults="updateResults"
        @searchResults="loading=true">
        </global-search>
      </div>
    </div>
    <div>
      <div class="tabs is-boxed is-fullwidth">
        <ul>
          <li :disabled="resultsCount[tab] === 0" 
          :class="[{'is-active': showTab(tab) && resultsCount[tab] !== 0 }, { 'is-disabled': resultsCount[tab] === 0 }]" 
          v-for="tab in tabs" @click="resultsCount[tab] !== 0 ? showTabType=tab : ''">
            <a v-show="!searchResultsFiltered[tab] || searchResultsFiltered[tab].length === resultsCount[tab]">
              {{ tab | capitalize }} ({{ resultsCount[tab] }})
            </a>
            <a v-show="searchResultsFiltered[tab] && searchResultsFiltered[tab].length !== resultsCount[tab]">
              {{ tab | capitalize }} ({{ resultsCount[tab] }})
              ({{ searchResultsFiltered[tab] ? searchResultsFiltered[tab].length : 0 }})
            </a>
          </li>
        </ul>
      </div>
      <loader v-show="loading"></loader>
      <div v-show="!loading">
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
          <table class="table is-fullwidth">
            <thead>
              <tr>
                <th>Organism</th><th>Model</th><th>Compartment</th>
                <th>ID</th><th>Name</th><th>Formula</th><th>Mass</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in searchResultsFiltered['metabolite']">
                <td>{{ item.organism | capitalize }}</td>
                <td>HMR2.00</td>
                <td>{{ item.compartment | capitalize }}</td>
                <td>
                  <a @click="viewComponentInfo(item.id, 4)">{{ item.id }}</a>
                </td>
                <td>{{ item.short_name }}</td>
                <td v-html="formulaFormater(item.formula)"></td>
                <td v-html="item.metabolite && item.metabolite.mass ? item.metabolite.mass + '&nbsp;g/mol' : ''"></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-show="showTab('enzyme') && resultsCount['enzyme'] !== 0">
          <div class="columns">
            <div class="column">
              <table class="table is-fullwidth">
                <thead>
                  <tr>
                    <th>Organism</th><th>Model</th><th>Compartment</th><th>ID</th>
                    <th>Name</th><th>Uniprot ID</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in searchResults['enzyme']">
                    <td>{{ item.organism | capitalize }}</td>
                    <td>HMR2.00</td>
                    <td>{{ item.compartment | capitalize }}</td>
                    <td>
                      <a @click="viewComponentInfo(item.id, 3)">{{ item.id }}</a>
                    </td>
                    <td>{{ item.short_name }}</td>
                    <td>{{ item.enzyme ? item.enzyme.uniprot_acc : '' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div v-show="showTab('reaction') && resultsCount['reaction'] !== 0">
          <div class="columns">
            <div class="column">
              <table class="table is-fullwidth">
                <thead>
                  <tr>
                    <th>Organism</th><th>Model</th><th>Subsystem</th><th>Compartment</th>
                    <th>ID</th><th>Equation</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in searchResults['reaction']">
                    <td>{{ item.organism ? item.organism : 'Human' | capitalize}}</td>
                    <td>HMR2.00</td>
                    <td>
                      <template v-for="sub, index in item.subsystem">
                        <a @click="viewComponentInfo(sub[1], 6)">{{ index != 0 ? '; ' : '' }}{{ sub[1] | capitalize }}</a>
                      </template>
                    </td>
                    <td>{{ item.compartment | capitalize }}</td>
                    <td>
                      <a @click="viewComponentInfo(item.id, 5)">{{ item.id }}</a>
                    </td>
                    <td>{{ item.equation }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div v-show="showTab('subsystem') && resultsCount['subsystem'] !== 0">
          <div class="columns">
            <div class="column">
              <table class="table is-fullwidth">
                <thead>
                  <tr>
                    <th>Organism</th><th>Model</th><th>Subsystem</th><th>System</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in searchResults['subsystem']">
                    <td>{{ item.organism ? item.organism : 'Human' | capitalize }}</td>
                    <td>HMR2.00</td>
                    <td><a @click="viewComponentInfo(item.name, 6)">{{ item.name | capitalize }}</a></td>
                    <td>{{ item.system | capitalize }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div v-show="showTab('compartment') && resultsCount['compartment'] !== 0">
          <div class="columns">
            <div class="column">
              <table class="table is-fullwidth">
                <thead>
                  <tr>
                    <th>Organism</th><th>Model</th><th>Compartment</th><th>View</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in searchResults['compartment']">
                    <td>{{ item.organism ? item.organism : 'Human' | capitalize }}</td>
                    <td>HMR2.00</td>
                    <td>{{ item.name | capitalize }}</td>
                    <td>
                      <div class="button" @click="viewCompartmentSVG(item.name)">
                        <span class="fa fa-eye"></span>
                      </div>
                    </td>
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
  </div>
</template>

<script>
import GlobalSearch from 'components/GlobalSearch';
import $ from 'jquery';
import Loader from 'components/Loader';
import router from '../router';
import { chemicalFormula } from '../helpers/chemical-formatters';
import EventBus from '../event-bus';

export default {
  name: 'search-table',
  components: {
    GlobalSearch,
    Loader,
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
      filters: {},
      searchTerm: 'metabolite',
      searchResults: {},
      showTabType: '',
      loading: true,
    };
  },
  computed: {
    searchResultsFiltered() {
      if (!this.searchResults) {
        return {};
      }
      const arr = JSON.parse(JSON.stringify(this.searchResults));
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
      for (const el of Object.keys(this.searchResults)) {
        if (el in this.resultsCount) {
          this.resultsCount[el] = this.searchResults[el].length;
        }
      }
    },
    fillFilterFields() {
      // get the otion values of the <select> in the filter panels
      // reset filter
      const newFilter = {
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
      };

      // store choice only once in a dict
      for (const componentType of Object.keys(this.searchResults)) {
        const compoList = this.searchResults[componentType];
        for (const el of compoList) {
          for (const field of Object.keys(newFilter[componentType])) {
            newFilter[componentType][field][el[field]] = 1;
          }
        }
      }

      // convert dict in array ad add 'None' if more than one choice
      for (const kType of Object.keys(newFilter)) {
        let validFilter = false;
        const fields = newFilter[kType];
        for (const kComp of Object.keys(fields)) {
          const values = fields[kComp];
          if (Object.keys(values).length === 1) {
            newFilter[kType][kComp] = Object.keys(values);
          } else {
            newFilter[kType][kComp] = ['None'].concat(Object.keys(values).sort());
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
      this.filters = newFilter;
      this.resetFilters();
    },
    updateResults(term, val) {
      this.loading = false;
      this.searchTerm = term;
      this.searchResultsFiltered = {};
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
      const newActiveFilters = JSON.parse(JSON.stringify(this.activeFilters));
      if (value === 'none') {
        delete newActiveFilters[type][compo];
      } else {
        newActiveFilters[type][compo] = value;
      }
      // trigger changes in the computed property 'searchResultsFiltered'
      this.activeFilters = newActiveFilters;
    },
    showTab(elementType) {
      return this.showTabType === elementType;
    },
    viewComponentInfo(id, tabIndex) {
      router.push(
        {
          path: '/',
          query: {
            tab: tabIndex,
            id,
          },
        },
      );
    },
    viewCompartmentSVG(name) {
      if (name === 'cytosol') {
        name = 'cytosol_1';  // eslint-disable-line no-param-reassign
      }
      EventBus.$emit('requestViewer', 'compartment', name, '', []);
    },
    resetFilters() {
      for (const tabname of this.tabs) {
        this.toggleFilters[tabname] = false;
        this.activeFilters[tabname] = {};
        this.disabledFilters[tabname] = false;
      }

      // reset <select>
      $('div.box select').each(function f() {
        $(this).find('option').first().prop('selected', true);
      });
    },
  },
  created() {
    // init filter booleans
    this.resetFilters();
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
#search-table {
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
}

</style>
