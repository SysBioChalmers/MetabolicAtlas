<template>
  <section class="extended-section">
    <div class="container">
      <div id="search-table">
        <div class="columns">
          <div class="column has-text-centered">
            <h3 class="title is-3">Advanced search all integrated GEMs: <i>{{ searchTerm }}</i></h3>
          </div>
        </div>
        <div class="columns is-centered">
          <global-search :quickSearch="false" :searchTerm="searchTerm"
            @updateResults="updateResults" @searchResults="loading=true">
          </global-search>
        </div>
        <div>
          <div class="tabs is-boxed is-fullwidth" v-if="showTabType">
            <ul>
              <li :disabled="resultsCount[tab] === 0"
              :class="[{'is-active has-text-weight-semibold': showTab(tab) && resultsCount[tab] !== 0 }, { 'is-disabled': resultsCount[tab] === 0 }]"
              v-for="tab in tabs" @click="resultsCount[tab] !== 0 ? showTabType=tab : ''">
                <a class="is-capitalized">
                  {{ tab }}s&nbsp;
                  <span v-if="resultsCount[tab] !== 0">({{ resultsCount[tab] }})</span>
                </a>
              </li>
            </ul>
          </div>
          <loader v-show="loading && searchTerm !== ''"></loader>
          <div v-show="!loading">
            <template v-for="header in tabs">
              <div v-show="showTab(header) && resultsCount[header] !== 0">
                <vue-good-table
                  :columns="columns[header]" :rows="rows[header]" :lineNumbers="true"
                  :sort-options="{ enabled: true }" styleClass="vgt-table striped bordered"
                  paginationOptions="tablePaginationOpts">
                  <template slot="table-row" slot-scope="props">
                    <span v-if="['name', 'id'].includes(props.column.field)">
                      <router-link :to="{ path: `/explore/gem-browser/${props.row.model}/${header}/${props.row.id}` }">
                        {{ props.row.name || props.row.id }}
                      </router-link>
                    </span>
                    <span v-else-if="props.column.field == 'subsystem'">
                      <router-link v-for="sub in props.formattedRow[props.column.field]"
                      :to="{ path: `/explore/gem-browser/${props.row.model}/subsystem/${idfy(sub)}` }"> {{ sub }}</router-link>
                    </span>
                    <span v-else-if="Array.isArray(props.formattedRow[props.column.field])">
                      {{ props.formattedRow[props.column.field].join("; ") }}
                    </span>
                    <span v-else>
                      {{ props.formattedRow[props.column.field] }}
                    </span>
                  </template>
                </vue-good-table>
              </div>
            </template>
          </div>
          <div class="columns is-multiline" v-show="!loading && (!showTabType || searchTerm === '')">
            <div v-if="searchResults.length === 0" class="column is-offset-3 is-6 has-text-centered notification">
              {{ messages.searchNoResult }}
            </div>
            <div class="column is-offset-3 is-6 content">
              <p>You can search metabolites by:</p>
              <ul class="menu-list">
                <li>ID</li>
                <li>name</li>
                <li>formula</li>
                <li>HMDB ID, name</li>
                <li>KEGG ID</li>
              </ul>
              <p>Enzymes by:</p>
              <ul class="menu-list">
                <li>ID</li>
                <li>name</li>
                <li>Ensembl ID</li>
                <li>Uniprot ID, name</li>
                <li>KEGG ID</li>
              </ul>
              <p>Reactions by:</p>
              <ul class="menu-list">
                <li>ID</li>
                <li>equation:</li>
                <ul class="menu-list">
                  <li>e.g. malonyl-CoA[c] => acetyl-CoA[c] + CO2[c]</li>
                  <li>without specifying compartment e.g 2 ADP => AMP + ATP</li>
                </ul>
                <li>EC code</li>
                <li>SBO ID</li>
              </ul>
              <p>Subsystem and compartment by:</p>
              <ul class="menu-list">
                <li>name</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>

import GlobalSearch from 'components/explorer/GlobalSearch';
import Loader from 'components/Loader';
import { VueGoodTable } from 'vue-good-table';
import 'vue-good-table/dist/vue-good-table.css';
import { chemicalFormula } from '../../helpers/chemical-formatters';
import { idfy } from '../../helpers/utils';
import { default as messages } from '../../helpers/messages';

export default {
  name: 'search-table',
  components: {
    GlobalSearch,
    Loader,
    VueGoodTable,
  },
  data() {
    return {
      messages,
      tablePaginationOpts: {
        enabled: true,
        perPage: 50,
        position: 'both',
        perPageDropdown: [25, 50, 100, 200],
        dropdownAllowAll: false,
        setCurrentPage: 1,
        nextLabel: 'next',
        prevLabel: 'prev',
        rowsPerPageLabel: 'Rows per page',
        ofLabel: 'of',
      },
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
            sortable: true,
          }, {
            label: 'Name',
            field: 'name',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
            html: true,
          }, {
            label: 'Formula',
            field: 'formula',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
          }, {
            label: 'Compartment',
            field: 'compartment',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          }, {
            label: 'Currency?',
            field: 'is_currency',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          },
        ],
        enzyme: [
          { label: 'Model',
            field: 'model',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          }, {
            label: 'Name',
            field: 'name',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
          }, {
            label: 'Subsystem',
            field: 'subsystem',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          }, {
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
            sortable: true,
          }, {
            label: 'ID',
            field: 'id',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
            html: true,
          }, {
            label: 'Equation',
            field: 'equation',
            filterOptions: {
              enabled: true,
            },
            sortable: false,
          }, {
            label: 'EC',
            field: 'ec',
            filterOptions: {
              enabled: true,
            },
            sortable: false,
          }, {
            label: 'Subsystem',
            field: 'subsystem',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
              filterFn: this.filterSubsystem,
            },
            sortable: true,
            html: true,
          }, {
            label: 'Compartment',
            field: 'compartment',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          }, {
            label: 'Transport?',
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
            sortable: true,
          }, {
            label: 'Name',
            field: 'name',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
            html: true,
          }, {
            label: 'Compartment',
            field: 'compartment',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          }, {
            label: 'Metabolites',
            field: 'metaboliteCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          }, {
            label: 'Enzymes',
            field: 'enzymeCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          }, {
            label: 'Reactions',
            field: 'reactionCount',
            filterOptions: {
              enabled: false,
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
          {
            label: '# Metabolites',
            field: 'metaboliteCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
          {
            label: '# Enzymes',
            field: 'enzymeCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
          {
            label: '# Reactions',
            field: 'reactionCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
          {
            label: '# Subsystems',
            field: 'subsystemCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
        ],
      },
      resultsCount: {},
      searchTerm: '',
      searchResults: {},
      showTabType: '',
      loading: false,
      rows: {
        metabolite: [],
        enzyme: [],
        reaction: [],
        subsystem: [],
        compartment: [],
      },
    };
  },
  methods: {
    formulaFormater(s) {
      return chemicalFormula(s);
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
          model: {},
          compartment: {},
          is_currency: {},
        },
        enzyme: {
          model: {},
          subsystem: {},
          compartment: {},
        },
        reaction: {
          model: {},
          compartment: {},
          subsystem: {},
          is_transport: {},
        },
        subsystem: {
          model: {},
          compartment: {},
        },
        compartment: {
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
              name: el.name,
              formula: el.formula,
              // subsystem: el.subsystem,
              compartment: el.compartment,
              is_currency: el.is_currency ? 'Yes' : 'No',
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
              name: el.gene_name,
              subsystem: el.subsystem,
              compartment: el.compartment,
            });
          } else if (componentType === 'reaction') {
            const reactionSubsArr = [];
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (field === 'subsystem' && el[field]) {
                for (const subsystem of el[field].split('; ')) {
                  if (!(subsystem in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][subsystem] = 1;
                  }
                  reactionSubsArr.push(subsystem);
                }
              } else if (field === 'compartment' && el[field]) {
                for (const compartment of el[field].split(/[^a-zA-Z0-9 ]+/)) {
                  if (compartment.trim() &&
                    !(compartment.trim() in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][compartment.trim()] = 1;
                  }
                }
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              id: el.id,
              model: el.model,
              equation: el.equation,
              ec: el.ec,
              subsystem: reactionSubsArr,
              compartment: el.compartment,
              is_transport: el.is_transport ? 'Yes' : 'No',
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
              id: el.name_id,
              model: el.model,
              name: el.name,
              compartment: el.compartment,
              metaboliteCount: el.metabolite_count,
              enzymeCount: el.enzyme_count,
              reactionCount: el.reaction_count,
            });
          } else if (componentType === 'compartment') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              id: el.name_id,
              model: el.model,
              name: el.name,
              metaboliteCount: el.metabolite_count,
              enzymeCount: el.enzyme_count,
              reactionCount: el.reaction_count,
              subsystemCount: el.subsystem_count,
            });
          }
        }
        for (const field of Object.keys(filterTypeDropdown[componentType])) {
          if (field === 'model') {
            filterTypeDropdown[componentType][field] =
              Object.keys(filterTypeDropdown[componentType][field]).map(
                (e) => { const d = {}; d.text = e; d.value = e; return d; }
            );
          } else {
            filterTypeDropdown[componentType][field] =
              Object.keys(filterTypeDropdown[componentType][field]).map(
                (e) => {
                  let v = e;
                  if (v === 'true') {
                    v = 'Yes';
                  } else if (v === 'false') {
                    v = 'No';
                  }
                  return v;
                }
            ).sort();
          }
        }
      }
      // assign filter choices lists to the columns
      this.columns.metabolite[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.metabolite.model;
      this.columns.metabolite[3].filterOptions.filterDropdownItems =
          filterTypeDropdown.metabolite.compartment;
      this.columns.metabolite[4].filterOptions.filterDropdownItems =
          filterTypeDropdown.metabolite.is_currency;

      this.columns.enzyme[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.enzyme.model;
      this.columns.enzyme[3].filterOptions.filterDropdownItems =
          filterTypeDropdown.enzyme.compartment;

      this.columns.reaction[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.reaction.model;
      this.columns.reaction[4].filterOptions.filterDropdownItems =
          filterTypeDropdown.reaction.subsystem_str;
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
      this.rows = rows;
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
    filterSubsystem(data, s) {
      return data.indexOf(s) !== -1;
    },
    showTab(elementType) {
      return this.showTabType === elementType;
    },
    idfy,
  },
  beforeMount() {
    this.searchTerm = this.$route.query.term || '';
  },
  mounted() {
    if (this.searchTerm) {
      // trigger the search in child component (globalSearch)
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
