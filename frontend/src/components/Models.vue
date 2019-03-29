<template>
  <section class="section extended-section">
    <div class="container">
      <div v-if="errorMessage">
        {{ errorMessage }}
      </div>
      <div v-else>
        <span class="title">Integrated Genome-Scale Metabolic Models</span><br><br>
        <span class="is-size-5">
          These models are integrated into the Metabolic Atlas database - the models can be explored via {{ messages.gemBrowserName }}, {{ messages.mapViewerName }} and {{ messages.interPartName }}.
        </span><br><br>
        <div id="integrated" class="columns is-multiline is-variable is-6">
          <div class="column is-half" v-for="model in models">
            <div class="card is-size-5">
              <header class="card-header clickable has-background-primary-lighter" @click="getModelData(model.details.id)">
                <p class="card-header-title card-content has-text-weight-bold has-text-primary">
                  {{ model.name }} &ndash; {{ model.short_name }}
                </p>
                <div class="card-header-icon">
                  <span class="icon has-text-primary">
                    <i class="fa fa-plus-square"></i>
                  </span>
                </div>
              </header>
              <div class="card-content">
                <div class="columns is-multiline">
                  <div class="column is-4">
                    Reactions: {{ model.reaction_count }}<br>
                    Metabolites: {{ model.metabolite_count }}<br>
                    Enzymes: {{ model.enzyme_count }}
                  </div>
                  <div class="column is-8">
                    Condition: {{ model.details.condition }}<br>
                    Tissue/Cell type: {{ model.tissue }}
                  </div>
                  <div class="column is-4">
                    Date: {{ model.details.last_update || "n/a" }}<br>
                    <a :href="model.details.repo_name" target="_blank">
                      <span class="icon"><i class="fa fa-github fa-lg"></i></span>
                      GitHub
                    </a>
                  </div>
                  <div class="column is-8">
                    <router-link class="button is-info is-medium is-outlined" :to="{ path: `/explore/gem-browser/${model.database_name}` }">
                      <span class="icon is-large"><i class="fa fa-search-plus"></i></span>
                      <span>{{ messages.gemBrowserName }}</span>
                    </router-link>
                    <router-link class="button is-info is-medium is-outlined" :to="{ path: `/explore/map-viewer/${model.database_name}` }">
                      <span class="icon is-large"><i class="fa fa-map-o"></i></span>
                      <span>{{ messages.mapViewerName }}</span>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <span class="title">Genome-Scale Metabolic Models</span><br><br>
        <loader v-show="showLoader"></loader>
        <div v-if="GEMS.length != 0">
          <vue-good-table
            :columns="columns" :rows="GEMS"
            :sort-options="{ enabled: true }" styleClass="vgt-table striped bordered" :paginationOptions="tablePaginationOpts"
            @on-row-click="getModel">
          </vue-good-table>
        </div>
        <div v-else>
          <span v-if="!showLoader">No models available</span>
        </div>
        <br>
        <div id="gem-list-modal" class="modal" v-bind:class="{ 'is-active': showModelTable }">
          <div class="modal-background" @click="showModelTable = false"></div>
          <div class="modal-content column is-6-fullhd is-8-desktop is-10-tablet is-full-mobile has-background-white" v-on:keyup.esc="showModelTable = false" tabindex="0">
            <div id="modal-info" class="model-table">
              <h2 class="title">
                {{ selectedModel.set_name}} - {{ selectedModel.label || selectedModel.tissue}}
              </h2>
              {{ selectedModel.description }}<br><br>
              <table class="table main-table">
                <tbody>
                  <tr v-for="field in model_fields" v-if="selectedModel[field.name]">
                    <td v-html="field.display" class="td-key has-background-primary has-text-white-bis"></td>
                    <td v-if="typeof(selectedModel[field.name]) === 'boolean'">
                      {{ selectedModel[field.name] ? 'Yes' : 'No' }}
                    </td>
                    <td v-else>
                      {{ selectedModel[field.name] }}
                    </td>
                  </tr>
                  <tr v-if="selectedModel.ref && selectedModel.ref.length !== 0">
                    <td class="td-key has-background-primary has-text-white-bis">Reference(s)</td>
                    <td>
                      <template v-for="oneRef in selectedModel.ref">
                        <p v-if="!oneRef.link">{{ oneRef.title }}</p>
                        <a v-else :href="oneRef.link" target="_blank">
                          {{ oneRef.title }} (PMID {{ oneRef.pubmed }})
                        </a>
                        <br>
                      </template>
                    </td>
                  </tr>
                </tbody>
              </table>
              <br>
              <span class="subtitle">Files</span>
              <table class="table">
                <tbody>
                  <tr>
                    <td v-for="file in selectedModel.files">
                      <a :href="file.path">{{ file.format }}</a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <button class="modal-close is-large" @click="showModelTable = false"></button>
        </div>
      </div>
    </div>
  </section>
</template>


<script>
import axios from 'axios';
import $ from 'jquery';
import { VueGoodTable } from 'vue-good-table';
import 'vue-good-table/dist/vue-good-table.css';
import Loader from 'components/Loader';
import { default as EventBus } from '../event-bus';
import { default as messages } from '../helpers/messages';

export default {
  name: 'gems',
  components: {
    Loader,
    VueGoodTable,
  },
  data() {
    return {
      columns: [
        {
          label: 'Set',
          field: 'set_name',
          filterOptions: {
            enabled: true,
            filterDropdownItems: [],
            filterFn: (a, b) => a === b,
          },
          sortable: true,
        }, {
          label: 'Organism',
          field: 'organism',
          filterOptions: {
            enabled: true,
          },
          sortable: true,
          html: true,
        }, {
          label: 'Label',
          field: 'label',
          filterOptions: {
            enabled: true,
          },
          sortable: true,
        }, {
          label: 'System',
          field: 'organ_system',
          filterOptions: {
            enabled: true,
            filterDropdownItems: [],
            filterFn: (a, b) => a === b,
          },
          sortable: true,
        }, {
          label: 'Condition',
          field: 'condition',
          filterOptions: {
            enabled: true,
            filterDropdownItems: [],
            filterFn: (a, b) => a === b,
          },
          sortable: true,
        }, {
          label: 'Tissue/Cell type',
          field: 'tissue',
          filterOptions: {
            enabled: true,
            filterFn: (a, b) => a.toLowerCase().includes(b.toLowerCase().trim()),
          },
          sortable: true,
        }, {
          label: 'Stats',
          field: 'stats',
          sortable: false,
          html: true,
        }, {
          label: 'Latest publication',
          field: 'year',
          filterOptions: {
            enabled: true,
          },
          sortable: true,
        }, {
          label: 'Maintained',
          field: 'maintained',
          filterOptions: {
            enabled: true,
            filterDropdownItems: ['Yes', 'No'],
          },
          sortable: true,
        },
      ],
      model_fields: [
        { name: 'organism', display: 'Organism' },
        { name: 'set_name', display: 'Set' },
        { name: 'organ_system', display: 'System' },
        { name: 'condition', display: 'Condition' },
        { name: 'tissue', display: 'Tissue' },
        { name: 'cell_type', display: 'Cell&nbsp;type' },
        { name: 'cell_line', display: 'Cell&nbsp;line' },
        { name: 'reaction_count', display: 'Reactions' },
        { name: 'metabolite_count', display: 'Metabolites' },
        { name: 'enzyme_count', display: 'Enzymes/genes' },
        { name: 'year', display: 'Year' },
        { name: 'maintained', display: 'Maintained' },
      ],
      selectedModel: {},
      errorMessage: '',
      GEMS: [],
      showModelTable: false,
      showLoader: false,
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
      messages,
      models: [],
    };
  },
  created() {
    EventBus.$on('viewGem', (modelID) => {
      this.getModelData(modelID);
    });
  },
  beforeMount() {
    this.getModelList();
    this.getModels();
  },
  methods: {
    getModelList() {
      // get models list
      axios.get('models/')
      .then((response) => {
        const models = {};
        for (const model of response.data) {
          model.tissue = [model.details.sample.tissue, model.details.sample.cell_type, model.details.sample.cell_line].filter(e => e).join(' ‒ ') || '-';
          models[model.database_name] = model;
        }
        this.models = models;
      })
      .catch(() => {
        this.errorMessage = messages.unknownError;
      });
    },
    getModel(params) {
      this.getModelData(params.row.id);
    },
    getModelData(id) {
      axios.get(`gems/${id}`)
      .then((response) => {
        const model = response.data;
        // reformat the dictionnary
        delete model.id;
        $.extend(model, model.sample);
        delete model.sample;
        const setDescription = model.gemodelset.description;
        delete model.gemodelset.description;
        model.gemodelset.set_name = model.gemodelset.name;
        delete model.gemodelset.name;
        if (model.ref.length === 0) {
          model.ref = model.gemodelset.reference;
        }
        delete model.gemodelset.reference;
        $.extend(model, model.gemodelset);
        delete model.gemodelset;
        if (!model.description) {
          model.description = setDescription;
        }

        this.selectedModel = model;
        this.showModelTable = true;
      })
      .catch(() => {
        this.showModelTable = false;
      });
    },
    getModels() {
      this.showLoader = true;
      axios.get('gems/')
      .then((response) => {
        this.GEMS = [];
        const setDropDownFilter = new Set();
        const systemDropDownFilter = new Set();
        const conditionDropDownFilter = new Set();
        for (let i = 0; i < response.data.length; i += 1) {
          const gem = response.data[i];
          const sample = gem.sample;
          delete gem.sample;
          const gemex = $.extend(gem, sample);
          gemex.tissue = [gemex.tissue, gemex.cell_type, gemex.cell_line].filter(e => e).join(' ‒ ') || '-';
          delete gemex.cell_type;
          gemex.stats = `reactions:&nbsp;${gem.reaction_count}<br>metabolites:&nbsp;${gemex.metabolite_count}<br>enzymes:&nbsp;${gemex.enzyme_count}`;
          delete gemex.reaction_count; delete gemex.enzyme_count; delete gemex.metabolite_count;
          gemex.maintained = gem.maintained ? 'Yes' : 'No';
          gemex.organ_system = gemex.organ_system || '-';
          gemex.condition = gemex.condition || '-';
          this.GEMS.push(gemex);

          // setup filters
          setDropDownFilter.add(gemex.set_name);
          systemDropDownFilter.add(gemex.organ_system);
          conditionDropDownFilter.add(gemex.condition);
        }
        this.columns[0].filterOptions.filterDropdownItems = Array.from(setDropDownFilter).sort();
        this.columns[3].filterOptions.filterDropdownItems = Array.from(systemDropDownFilter).sort();
        this.columns[4].filterOptions.filterDropdownItems =
          Array.from(conditionDropDownFilter).sort();

        this.errorMessage = '';
        this.showLoader = false;
      })
      .catch(() => {
        this.errorMessage = messages.notFoundError;
        this.showLoader = false;
      });
    },
    buildHeader() {
      if (this.selectedModel.label) {
        return ` <i>${this.selectedModel.organism}</i>: ${this.selectedModel.set_name} - ${this.selectedModel.label}`;
      }
      return ` <i>${this.selectedModel.organism}</i>: ${this.selectedModel.set_name} - ${this.selectedModel.tissue}`;
    },
  },
};

</script>

<style lang="scss"></style>
