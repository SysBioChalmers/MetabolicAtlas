<template>
  <section class="extended-section">
    <div class="container">
      <div id="search-table">
        <div class="columns">
          <div class="column has-text-centered">
            <h3 class="title is-3">Global search all integrated GEMs for <i>{{ searchTerm }}</i></h3>
          </div>
        </div>
        <div class="columns is-centered">
          <global-search :quickSearch="false" :searchTerm="searchTerm"
            @updateSearch="updateSearch" @searchResults="loading=true">
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
            <div v-if="searchResults.length === 0" class="column is-offset-3 is-6">
              <div v-if="searchTerm !== ''" class=" has-text-centered notification">
                {{ messages.searchNoResult }}
              </div>
              <div class="content">
                <p>This page provides search by the following parameters:</p>
                <p>Metabolites by:</p>
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
            <template v-for="header in tabs">
              <div v-show="showTab(header) && resultsCount[header] !== 0">
                <vue-good-table
                  :columns="columns[header]" :rows="rows[header]"
                  :sort-options="{ enabled: true }" styleClass="vgt-table striped bordered" :paginationOptions="tablePaginationOpts">
                  <template slot="table-row" slot-scope="props">
                    <template v-if="props.column.field == 'model'">
                      {{ props.formattedRow[props.column.field].name }}
                    </template>
                    <template v-else-if="['name', 'id'].includes(props.column.field)">
                      <router-link :to="{ path: `/explore/gem-browser/${props.row.model.id}/${header}/${props.row.id}` }">
                        {{ props.row.name || props.row.id }}
                      </router-link>
                    </template>
                    <template v-else-if="props.column.field == 'subsystem'">
                      <template v-for="(sub, i) in props.formattedRow[props.column.field]">
                        <template v-if="i != 0">; </template>
                        <router-link :to="{ path: `/explore/gem-browser/${props.row.model.id}/subsystem/${idfy(sub)}` }"> {{ sub }}</router-link>
                      </template>
                    </template>
                    <template v-else-if="props.column.field == 'compartment'">
                      <template v-if="['subsystem', 'enzyme'].includes(header)">
                        <template v-for="(comp, i) in props.formattedRow[props.column.field]">
                          <template v-if="i != 0">; </template>
                          <router-link :to="{ path: `/explore/gem-browser/${props.row.model.id}/compartment/${idfy(comp)}` }"> {{ comp }}</router-link>
                        </template>
                      </template>
                      <template v-else-if="header == 'reaction'">
                        <template v-for="(RP, i) in props.formattedRow[props.column.field].split(' => ')">
                          <template v-if="i != 0"> => </template>
                            <template v-for="(compo, j) in RP.split(' + ')">
                              <template v-if="j != 0"> + </template>
                              <router-link :to="{ path: `/explore/gem-browser/${props.row.model.id}/compartment/${idfy(compo)}` }"> {{ compo }}</router-link>
                            </template>
                        </template>
                      </template>
                      <template v-else-if="Array.isArray(props.formattedRow[props.column.field])">
                        {{ props.formattedRow[props.column.field].join("; ") }}
                      </template>
                      <template v-else>
                         <router-link :to="{ path: `/explore/gem-browser/${props.row.model.id}/compartment/${idfy(props.formattedRow[props.column.field])}` }"> {{ props.formattedRow[props.column.field] }}</router-link>
                      </template>
                    </template>
                    <template v-else-if="Array.isArray(props.formattedRow[props.column.field])">
                      {{ props.formattedRow[props.column.field].join("; ") }}
                    </template>
                    <template v-else>
                      {{ props.formattedRow[props.column.field] }}
                    </template>
                  </template>
                </vue-good-table>
              </div>
            </template>
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
              filterFn: (e, s) => e.id === s,
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
            label: 'Formula',
            field: 'formula',
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
        enzyme: [
          { label: 'Model',
            field: 'model',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
              filterFn: (e, s) => e.id === s,
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
              filterFn: (e, s) => e.id === s,
            },
            sortable: true,
          }, {
            label: 'ID',
            field: 'id',
            filterOptions: {
              enabled: true,
            },
            sortable: true,
          }, {
            label: 'Equation',
            field: 'equation',
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
              filterFn: (e, s) => e.id === s,
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
            label: 'Compartment',
            field: 'compartment',
            filterOptions: {
              enabled: true,
              filterDropdownItems: [],
            },
            sortable: true,
          }, {
            label: 'Metabolites',
            field: 'metabolite_count',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          }, {
            label: 'Enzymes',
            field: 'enzyme_count',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          }, {
            label: 'Reactions',
            field: 'reaction_count',
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
              filterFn: (e, s) => e.id === s,
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
            label: 'Metabolites',
            field: 'metaboliteCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
          {
            label: 'Enzymes',
            field: 'enzymeCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
          {
            label: 'Reactions',
            field: 'reactionCount',
            filterOptions: {
              enabled: false,
            },
            sortable: true,
          },
          {
            label: 'Subsystems',
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
      searchResults: [],
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
          // subsystem: {},
          compartment: {},
        },
        enzyme: {
          model: {},
          // subsystem: {},
          compartment: {},
        },
        reaction: {
          model: {},
          compartment: {},
          // subsystem: {},
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
              if (field === 'model') {
                filterTypeDropdown[componentType][field][el[field].id] = el[field].name;
              } else if (field === 'subsystem') {
                for (const v of el[field]) {
                  if (!(v in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][v] = 1;
                  }
                }
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              id: el.id,
              model: el.model,
              name: el.name,
              formula: el.formula,
              subsystem: el.subsystem,
              compartment: el.compartment,
            });
          } else if (componentType === 'enzyme') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (field === 'model') {
                filterTypeDropdown[componentType][field][el[field].id] = el[field].name;
              } else if (['compartment', 'subsystem'].includes(field)) {
                for (const v of el[field]) {
                  if (!(v in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][v] = 1;
                  }
                }
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
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
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (field === 'subsystem' && el[field]) {
                for (const v of el[field]) {
                  if (!(v in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][v] = 1;
                  }
                }
              } else if (field === 'compartment' && el[field]) {
                for (const compartment of el[field].split(/[^a-zA-Z0-9 ]+/)) {
                  if (compartment.trim() &&
                    !(compartment.trim() in filterTypeDropdown[componentType][field])) {
                    filterTypeDropdown[componentType][field][compartment.trim()] = 1;
                  }
                }
              } else if (field === 'model') {
                filterTypeDropdown[componentType][field][el[field].id] = el[field].name;
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              id: el.id,
              model: el.model,
              equation: el.equation_wname,
              subsystem: el.subsystem,
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
              } else if (field === 'model') {
                filterTypeDropdown[componentType][field][el[field].id] = el[field].name;
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
                filterTypeDropdown[componentType][field][el[field]] = 1;
              }
            }
            rows[componentType].push({
              id: el.name_id,
              model: el.model,
              name: el.name,
              compartment: el.compartment,
              metabolite_count: el.metabolite_count,
              enzyme_count: el.enzyme_count,
              reaction_count: el.reaction_count,
            });
          } else if (componentType === 'compartment') {
            for (const field of Object.keys(filterTypeDropdown[componentType])) {
              if (field === 'model') {
                filterTypeDropdown[componentType][field][el[field].id] = el[field].name;
              } else if (!(el[field] in filterTypeDropdown[componentType][field])) {
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
                (e) => { const d = {}; d.value = e; d.text = filterTypeDropdown[componentType][field][e]; return d; } // eslint-disable-line
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
          filterTypeDropdown.metabolite.subsystem;
      this.columns.metabolite[4].filterOptions.filterDropdownItems =
          filterTypeDropdown.metabolite.compartment;

      this.columns.enzyme[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.enzyme.model;
      this.columns.enzyme[3].filterOptions.filterDropdownItems =
          filterTypeDropdown.enzyme.compartment;

      this.columns.reaction[0].filterOptions.filterDropdownItems =
          filterTypeDropdown.reaction.model;
      // this.columns.reaction[3].filterOptions.filterDropdownItems =
      //     filterTypeDropdown.reaction.subsystem;
      this.columns.reaction[4].filterOptions.filterDropdownItems =
          filterTypeDropdown.reaction.compartment;
      this.columns.reaction[5].filterOptions.filterDropdownItems =
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
    updateSearch(term, results) {
      this.searchTerm = term;
      this.$router.push({
        name: 'search',
        query: {
          term: this.searchTerm,
        },
      });
      this.loading = false;
      this.searchResultsFiltered = {};
      this.searchResults = results;
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
    showTab(elementType) {
      return this.showTabType === elementType;
    },
    idfy,
    chemicalFormula,
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
