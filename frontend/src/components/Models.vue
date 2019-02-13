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
          <div class="column is-6" v-for="model in models">
            <div class="card is-size-5">
            <header class="card-header has-background-primary">
              <p class="card-content has-text-weight-bold has-text-white">{{ model.name }}</p>
            </header>
            <div class="card-content">
              <div class="content">
                Authors: {{ model.authors }}<br>
                Year: {{ model.year }}<br>
                # enzymes: {{ model.enzyme_count }}<br>
                # metabolite: {{ model.metabolite_count }}<br>
                # reactions: {{ model.reaction_count }}<br>
              </div>
            </div>
          </div>
          </div>
        </div>
        <span class="title">Genome-Scale Metabolic Models</span><br><br>
        <loader v-show="showLoader"></loader>
        <div v-if="GEMS.length != 0">
          <vue-good-table
            :columns="columns" :rows="GEMS" :lineNumbers="true"
            :sort-options="{ enabled: true }" styleClass="vgt-table striped bordered" :paginationOptions="tablePaginationOpts"
            @on-row-click="getModel">
          </vue-good-table>
        </div>
        <div v-else>
          <span v-if="!showLoader">No models available</span>
        </div>
        <br>
        <div class="modal" v-bind:class="{ 'is-active': showModelTable }">
          <div class="modal-background" @click="showModelTable = false"></div>
          <div class="modal-content">
            <div id="modal-info" class="model-table">
              <span class="title is is-primary" v-html="buildHeader()"></span>
              {{ selectedModel.description }}<br><br>
              <table class="table main-table">
                <tbody>
                  <tr v-for="field in model_fields" v-if="selectedModel[field.name]">
                    <td v-html="field.display" class="td-key has-background-primary has-text-white-bis"></td>
                    <td v-if="typeof(selectedModel[field.name]) === 'boolean'">
                      {{ selectedModel[field.name] ? 'yes' : 'No' }}
                    </td>
                    <td v-else>
                      {{ selectedModel[field.name] }}
                    </td>
                  </tr>
                  <tr v-if="selectedModel.ref && selectedModel.ref.length !== 0">
                    <td class="td-key">Reference</td>
                    <td v-if="selectedModel.ref[0].link">
                      <a :href="selectedModel.ref[0].link" target="_blank" v-html="getReferenceLink(selectedModel.ref[0])">
                      </a>
                    </td>
                    <td v-else>
                        {{ selectedModel.ref.title }}
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
            // filterDropdownItems: [],
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
          },
          sortable: true,
        }, {
          label: 'Condition',
          field: 'condition',
          filterOptions: {
            enabled: true,
          },
          sortable: true,
        }, {
          label: 'Tissue/Cell type',
          field: 'tissue',
          filterOptions: {
            enabled: true,
          },
          sortable: true,
        }, {
          label: '# reactions',
          field: 'reaction_count',
          filterOptions: {
            enabled: true,
          },
          sortable: true,
        }, {
          label: '# metabolites',
          field: 'metabolite_count',
          filterOptions: {
            enabled: true,
          },
          sortable: true,
        }, {
          label: '# enzymes',
          field: 'enzyme_count',
          filterOptions: {
            enabled: true,
          },
          sortable: true,
        }, {
          label: 'Year',
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
        { name: 'reaction_count', display: '#&nbsp;reactions' },
        { name: 'metabolite_count', display: '#&nbsp;metabolites' },
        { name: 'enzyme_count', display: '#&nbsp;enzymes/genes' },
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
      this.getModel(modelID);
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
            models[model.database_name] = model;
          }
          this.models = models;
        })
        .catch(() => {
          this.errorMessage = messages.unknownError;
        });
    },
    getModel(params) {
      const id = params.row.id;
      axios.get(`gems/${id}`)
      .then((response) => {
        let model = response.data;
        // reformat the dictionnary
        delete model.id;
        model = $.extend(model, model.sample);
        delete model.sample;
        const setDescription = model.gemodelset.description;
        delete model.gemodelset.description;
        model.gemodelset.set_name = model.gemodelset.name;
        delete model.gemodelset.name;
        delete model.gemodelset.reference;
        model = $.extend(model, model.gemodelset);
        delete model.gemodelset;
        // model = $.extend(model, model.reference);
        // delete model.reference;
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
        for (let i = 0; i < response.data.length; i += 1) {
          const gem = response.data[i];
          const sample = gem.sample;
          delete gem.sample;
          const gemex = $.extend(gem, sample);
          if (gemex.tissue && gemex.cell_type && gemex.cell_line) {
            gemex.tissue = `${gemex.tissue} - ${gemex.cell_type} - ${gemex.cell_line}`;
          } else if (gemex.tissue && gemex.cell_line) {
            gemex.tissue = `${gemex.tissue} - ${gemex.cell_line}`;
          } else if (gemex.cell_type && gemex.cell_line) {
            gemex.tissue = `${gemex.cell_type} - ${gemex.cell_line}`;
          } else if (gemex.cell_type) {
            gemex.tissue = gemex.cell_type;
          }
          delete gemex.cell_type;
          gemex.maintained = gem.maintained ? 'Yes' : 'No';
          this.GEMS.push(gemex);
        }
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
    getReferenceLink(ref) {
      const title = ref.title.replace(/&lt;/g, '<').replace(/&gt;/g, '>');
      if (ref.pubmed) {
        return `${title} (PMID: ${ref.pubmed})`;
      }
      return title;
    },
  },
};

</script>

<style lang="scss">
#integrated {
  .card {
    height: 100%;
  }
}
</style>
