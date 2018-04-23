<template>
  <div id="search-table">
    <div class="container columns">
      <global-search class="is-offset-2"
      :quickSearch=false
      :searchTerm=searchTerm
      @updateResults="updateResults"
      @searchResults="loading=true">
      </global-search>
    </div>
    <div>
      <div class="tabs is-boxed is-fullwidth">
        <ul>
          <li :disabled="resultsCount[tab] === 0" 
          :class="[{'is-active': showTab(tab) && resultsCount[tab] !== 0 }, { 'is-disabled': resultsCount[tab] === 0 }]" 
          v-for="tab in tabs" @click="resultsCount[tab] !== 0 ? showTabType=tab : ''">
            <a>
              {{ tab | capitalize }} ({{ resultsCount[tab] }})
            </a>
          </li>
        </ul>
      </div>
      <loader v-show="loading"></loader>
      <div v-show="!loading">
        <div v-show="showTab('metabolite') && resultsCount['metabolite'] !== 0">
          <good-table
                :columns="columns['metabolite']"
                :rows="rows['metabolite']"
                :lineNumbers="true"
                :sort-options="{
                  enabled: true,
                  initialSortBy: {field: 'name', type: 'asc'}
                }"
                styleClass="vgt-table striped bordered">
          </good-table>
        </div>
        <div v-show="showTab('enzyme') && resultsCount['enzyme'] !== 0">
          <good-table
            :columns="columns['enzyme']"
            :rows="rows['enzyme']"
            :lineNumbers="true"
            :sort-options="{
              enabled: true,
              initialSortBy: {field: 'name', type: 'asc'}
            }"
            styleClass="vgt-table striped bordered">
          </good-table>
        </div>
        <div v-show="showTab('reaction') && resultsCount['reaction'] !== 0">
          <good-table
            :columns="columns['reaction']"
            :rows="rows['reaction']"
            :lineNumbers="true"
            :sort-options="{
              enabled: true,
              initialSortBy: {field: 'equation', type: 'asc'}
            }"
            styleClass="vgt-table striped bordered">
          </good-table>
        </div>
        <div v-show="showTab('subsystem') && resultsCount['subsystem'] !== 0">
          <good-table
            :columns="columns['subsystem']"
            :rows="rows['subsystem']"
            :lineNumbers="true"
            :sort-options="{
              enabled: true,
              initialSortBy: {field: 'name', type: 'asc'}
            }"
            styleClass="vgt-table striped bordered">
          </good-table>
        </div>
        <div v-show="showTab('compartment') && resultsCount['compartment'] !== 0">
          <good-table
            :columns="columns['compartment']"
            :rows="rows['compartment']"
            :lineNumbers="true"
            :sort-options="{
              enabled: true,
              initialSortBy: {field: 'name', type: 'asc'}
            }"
            styleClass="vgt-table striped bordered">
          </good-table>
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
// import Vue from 'vue';
import GlobalSearch from 'components/GlobalSearch';
// import $ from 'jquery';
import Loader from 'components/Loader';
import { GoodTable } from 'vue-good-table';
import 'vue-good-table/dist/vue-good-table.css';
import { chemicalFormula } from '../helpers/chemical-formatters';
import EventBus from '../event-bus';

// Vue.use(VueGoodTable);

export default {
  name: 'search-table',
  components: {
    GlobalSearch,
    Loader,
    GoodTable,
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
      columns: {
        metabolite: [
          {
            label: 'Model',
            field: 'model',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            formatFn: this.getDisplayModelName,
            sortable: true,
          },
          {
            label: 'Name',
            field: this.formatMetaboliteNameCell,
            filterOptions: {
              enabled: true,
              filterFn: this.filterLink,
            },
            sortable: true,
            html: true,
          },
          {
            label: 'Formula',
            field: 'formula',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
          },
          {
            label: 'Compartment',
            field: 'compartment',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          },
        ],
        enzyme: [
          {
            label: 'Model',
            field: 'model',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            formatFn: this.getDisplayModelName,
            sortable: true,
          },
          {
            label: 'Name',
            field: this.formatEnzymeNameCell,
            filterOptions: {
              enabled: true,
              filterFn: this.filterLink,
            },
            sortable: true,
            html: true,
          },
          {
            label: 'Ensembl ID',
            field: 'ensembl',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
          },
          {
            label: 'Uniprot ID',
            field: 'uniprot',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
          },
          {
            label: 'Compartment',
            field: 'compartment',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          },
        ],
        reaction: [
          {
            label: 'Model',
            field: 'model',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            formatFn: this.getDisplayModelName,
            sortable: true,
          },
          {
            label: 'ID',
            // field: this.formatReactionNameCell,
            field: 'id',
            filterOptions: {
              enabled: true,
              filterFn: this.filterLink,
            },
            sortable: true,
            html: true,
          },
          {
            label: 'Equation',
            field: 'equation',
            filterOptions: {
              enabled: true,
            },
            sortable: false,
          },
          {
            label: 'EC',
            field: 'ec',
            filterOptions: {
              enabled: true,
            },
            sortable: false,
          },
          {
            label: 'Subsystem',
            field: this.formatSubsystemArrCell,
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
              filterFn: this.filterSubsystem,
            },
            sortable: true,
            html: true,
          },
          {
            label: 'Compartment',
            field: 'compartment',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          },
          {
            label: 'Is transport',
            field: 'is_transport',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: false,
          },
        ],
        subsystem: [
          {
            label: 'Model',
            field: 'model',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            formatFn: this.getDisplayModelName,
            sortable: true,
          },
          {
            label: 'Name',
            field: 'name',
            filterOptions: {
              enabled: true,
              filterFn: this.filterLink,
            },
            sortable: true,
            html: true,
          },
          {
            label: 'System',
            field: 'system',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          },
          {
            label: 'Compartment',
            field: this.formatCompartmentArrCell,
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          },
        ],
        compartment: [
          {
            label: 'Model',
            field: 'model',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            formatFn: this.getDisplayModelName,
            sortable: true,
          },
          {
            label: 'Name',
            field: 'name',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
        ],
      },
      resultsCount: {},
      filters: {},
      searchTerm: 'metabolite',
      searchResults: {},
      showTabType: '',
      loading: true,
      rows: {
        metabolite: [],
        enzyme: [],
        reaction: [],
        subsystem: [],
        compartment: [],
      },
    };
  },
  computed: {
    // searchResultsFiltered() {
    //   if (!this.searchResults) {
    //     return {};
    //   }
    //   const arr = JSON.parse(JSON.stringify(this.searchResults));
    //   for (const key of Object.keys(this.activeFilters)) {
    //     for (const compo of Object.keys(this.activeFilters[key])) {
    //       const val = this.activeFilters[key][compo];
    //       arr[key] = arr[key].filter(el => el[compo].toLowerCase() === val.toLowerCase());
    //     }
    //   }
    //   return arr;
    // },
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
      const filterTypeDropdown = {
        metabolite: {
          // organism: {},
          model: {},
          compartment: {},
          // subsystem: [],
        },
        enzyme: {
          // organism: {},
          model: {},
          compartment: {},
          subsystem: {},
        },
        reaction: {
          // organism: {},
          model: {},
          compartment: {},
          subsystem: {},
          is_transport: {},
        },
        subsystem: {
          // organism: {},
          model: {},
          system: {},
          compartment: {},
        },
        compartment: {
          // organism: [],
          model: {},
        },
      };

      const rows = {
        metabolite: [],
        enzyme: [],
        reaction: [],
        subsystem: [],
        compartment: [],
      };

      // store choice only once in a dict
      for (const componentType of Object.keys(this.searchResults)) {
        const compoList = this.searchResults[componentType];
        for (const el of compoList) { // e.g. results list for metabolites
          if (componentType === 'metabolite') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }

            rows[componentType].push({
              id: el.id,
              model: el.model,
              name: el.short_name,
              formula: el.formula,
              // subsystem: el.subsystem,
              compartment: el.compartment,
            });
          } else if (componentType === 'enzyme') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              id: el.id,
              model: el.model,
              name: el.short_name,
              ensembl: el.long_name,
              uniprot: el.enzyme ? el.enzyme.uniprot_acc : '',
              compartment: el.compartment,
            });
          } else if (componentType === 'reaction') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (field === 'subsystem') {
                for (const subsystem of el[field]) {
                  if (!(subsystem[1] in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][subsystem[1]] = 1;
                  }
                }
              } else if (field === 'compartment') {
                for (const compartment of el[field].split(/[^a-zA-Z0-9 ]+/)) {
                  if (!(compartment.trim() in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][compartment.trim()] = 1;
                  }
                }
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            console.log(filterTypeDropdown[componentType].subsystem);
            rows[componentType].push({
              id: `<a href="/GemsExplorer/${el.model}/reaction/${el.id}">${el.id}</a>`,
              model: el.model,
              equation: el.equation,
              ec: el.ec,
              subsystem: el.subsystem,
              compartment: el.compartment,
              is_transport: el.is_transport,
            });
          } else if (componentType === 'subsystem') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (field === 'compartment') {
                for (const compartment of el[field]) {
                  if (!(compartment in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][compartment] = 1;
                  }
                }
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              model: el.model,
              name: `<a href="/GemsExplorer/${el.model}/subsystem/${el.name}">${el.name}</a>`,
              system: el.system,
              compartment: el.compartment,
            });
          } else if (componentType === 'compartment') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              model: el.model,
              name: el.name,
              metaboliteCount: el.nr_metabolites,
              enzymeCount: el.nr_enzymes,
              reactionCount: el.nr_reactions,
              subsystemCount: el.nr_subsystems,
            });
          }
        }
        for (const field of Object.keys(filterTypeDropdown[componentType])) {
          if (field === 'model') {
            filterTypeDropdown[componentType][field] =
              Object.keys(filterTypeDropdown[componentType][field]).map(
                (e) => { const d = {}; d.text = this.$t(e); d.value = e; return d; }
            );
          } else {
            filterTypeDropdown[componentType][field] =
              Object.keys(filterTypeDropdown[componentType][field]).map(
                (e) => { const d = {}; d.text = e; d.value = e; return d; }
            );
          }
        }
      }
      this.columns.metabolite[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.metabolite.model;
      this.columns.metabolite[3].filterOptions.filterDropdownItems =
          filterTypeDropdown.metabolite.compartment;

      this.columns.enzyme[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.enzyme.model;
      this.columns.enzyme[4].filterOptions.filterDropdownItems =
          filterTypeDropdown.enzyme.compartment;

      this.columns.reaction[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.reaction.model;
      this.columns.reaction[4].filterOptions.filterDropdownItems =
          filterTypeDropdown.reaction.subsystem;
      this.columns.reaction[5].filterOptions.filterDropdownItems =
          filterTypeDropdown.reaction.compartment;
      this.columns.reaction[6].filterOptions.filterDropdownItems =
          filterTypeDropdown.reaction.is_transport;

      this.columns.subsystem[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.subsystem.model;
      this.columns.subsystem[2].filterOptions.filterDropdownItems =
          filterTypeDropdown.subsystem.system;
      this.columns.subsystem[3].filterOptions.filterDropdownItems =
          filterTypeDropdown.subsystem.compartment;

      this.columns.compartment[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.subsystem.model;
      // convert dict in array ad add 'None' if more than one choice
      // for (const kType of Object.keys(newFilter)) {
      //   let validFilter = false;
      //   const fields = newFilter[kType];
      //   for (const kComp of Object.keys(fields)) {
      //     const values = fields[kComp];
      //     if (Object.keys(values).length === 1) {
      //       newFilter[kType][kComp] = Object.keys(values);
      //     } else {
      //       newFilter[kType][kComp] = ['None'].concat(Object.keys(values).sort());
      //       validFilter = true;
      //     }
      //   }
      //   if (!validFilter) {
      //     // of all filter contains only one choice
      //     // desactivate the filter panel
      //     this.disabledFilters[kType] = true;
      //     this.toggleFilters[kType] = false;
      //   }
      // }
      // this.filters = filterTypeDropdown;
      this.rows = rows;


      // this.rows = {
      //   metabolite: [
      //     { id: 1, organism: 'none', name: 'test1', formula: 'fornula1', compartment: 'none' },
      //     { id: 2, organism: 'none', name: 'test2', formula: 'fornula2', compartment: 'none' },
      //     { id: 3, organism: 'none', name: 'test3', formula: 'fornula3', compartment: 'none' },
      //   ],
      // };

      // this.columns.metabolite[1].filterOptions.filterDropdownItems = [];
      // this.columns.metabolite[4].filterOptions.filterDropdownItems = [];

      // this.filters2 = newFilter2;
      // this.resetFilters();
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
    getDisplayModelName(v) {
      return this.$t(v);
    },
    formatMetaboliteNameCell(row) {
      return `<a href="/GemsExplorer/${row.model}/metabolite/${row.id}">${row.name}</a>`;
    },
    formatEnzymeNameCell(row) {
      return `<a href="/GemsExplorer/${row.model}/enzyme/${row.id}">${row.name}</a>`;
    },
    formatReactionNameCell(row) {
      return `<a href="/GemsExplorer/${row.model}/reaction/${row.id}">${row.id}</a>`;
    },
    formatSubsystemArrCell(row) {
      let s = '';
      for (const subsystem of row.subsystem) {
        s += `<a href="/GemsExplorer/${row.model}/subsystem/${subsystem[1]}">${subsystem[1]}</a>; `;
      }
      return s.slice(0, -2);
    },
    formatCompartmentArrCell(row) {
      return row.compartment.join('; ');
    },
    filterLink(data, s) {
      console.log('call filterLink');
      return data.split('>')[1].split('<')[0].toLowerCase().indexOf(s.toLowerCase()) !== -1;
    },
    filterSubsystem(data, s) {
      return data.indexOf(s) !== -1;
    },
    // doFilterResults(type, compo, event) {
    //   const select = event.srcElement;
    //   const value = select.options[select.selectedIndex].innerHTML.trim().toLowerCase();

    //   // copy the dict of filter to trigger the change
    //   const newActiveFilters = JSON.parse(JSON.stringify(this.activeFilters));
    //   if (value === 'none') {
    //     delete newActiveFilters[type][compo];
    //   } else {
    //     newActiveFilters[type][compo] = value;
    //   }
    //   // trigger changes in the computed property 'searchResultsFiltered'
    //   this.activeFilters = newActiveFilters;
    // },
    showTab(elementType) {
      return this.showTabType === elementType;
    },
    viewComponentInfo(type, id) {
      EventBus.$emit('updateSelTab', type, id);
    },
    viewCompartmentSVG(name) {
      if (name === 'cytosol') {
        name = 'cytosol_1';  // eslint-disable-line no-param-reassign
      }
      EventBus.$emit('requestViewer', 'compartment', name, '', []);
    },
    // resetFilters() {
    //   for (const tabname of this.tabs) {
    //     this.toggleFilters[tabname] = false;
    //     this.activeFilters[tabname] = {};
    //     this.disabledFilters[tabname] = false;
    //   }

    //   // reset <select>
    //   $('div.box select').each(function f() {
    //     $(this).find('option').first().prop('selected', true);
    //   });
    // },
  },
  created() {
    // init filter booleans
    // this.resetFilters();
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
