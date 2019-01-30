<template>
  <section class="section extended-section">
    <div class="container">
      <div v-if="errorMessage">
        {{ errorMessage }}
      </div>
      <div v-else id="models">
        <span class="title">Genome-Scale Metabolic Models</span>
        <br>
        <div class="container">
          <loader v-show="showLoader"></loader>
          <div v-if="sortedGEMS.length != 0">
            <div class="columns">
              <div class="column">
                <span id="show-m-but" class="button is-light" :class="{'is-active': showMaintained }"
                  @click="toggleMaintainedModels">
                  Maintained models only
                </span>
              </div>
            </div>
            <div class="columns">
              <div class="column is-full">
                <table class="table is-bordered is-striped is-narrow is-fullwidth" v-if="filteredOldGEMS.length != 0">
                  <thead>
                    <tr style="background: #F8F4F4">
                      <th v-for="f in fields" v-html="f.display" :width="f.width ? f.width : ''"
                        @click="sortBy(f.name)">
                        </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr class="m-row" v-for="gem in filteredOldGEMS"
                      @click="getModel(gem.id)">
                      <td v-for="i in fields.length">
                        {{ gem[fields[i-1].name] }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div v-else>
            <span v-if="!showLoader">No models available</span>
          </div>
        </div>
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
          <button class="modal-close" @click="showModelTable = false"></button>
        </div>
      </div>
    </div>
  </section>
</template>


<script>
import axios from 'axios';
import $ from 'jquery';
import Loader from 'components/Loader';
import { default as compare } from '../helpers/compare';
import { default as EventBus } from '../event-bus';
import { default as messages } from '../helpers/messages';

export default {
  name: 'gems',
  components: {
    Loader,
  },
  data() {
    return {
      fields: [
        { name: 'set_name', display: 'Set' },
        { name: 'organism', display: 'Organism' },
        { name: 'label', display: 'Label' },
        // { name: 'organ_system', display: 'System' },
        { name: 'condition', display: 'Condition' },
        { name: 'tissue', display: 'Tissue/Cell&nbsp;type' },
        { name: 'reaction_count', display: '#&nbsp;reactions', width: 100 },
        { name: 'metabolite_count', display: '#&nbsp;metabolites', width: 100 },
        { name: 'enzyme_count', display: '#&nbsp;enzymes', width: 100 },
        { name: 'year', display: 'Year', width: 70 },
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
      sortAsc: true,
      errorMessage: '',
      GEMS: [],
      sortedGEMS: [],
      showMaintained: false,
      showModelTable: false,
      showLoader: false,
    };
  },
  computed: {
    filteredOldGEMS: function f() {
      return this.showMaintained ?
       this.sortedGEMS.filter(el => el.maintained) : this.sortedGEMS;
    },
  },
  created() {
    EventBus.$on('viewGem', (modelID) => {
      this.getModel(modelID);
    });
  },
  beforeMount() {
    this.getModels();
  },
  methods: {
    getModel(id) {
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
          this.GEMS.push(gemex);
        }
        this.sortedGEMS = this.GEMS.sort(
          compare('set_name', null, 'asc'));
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
    sortBy(field) {
      const gemsList = Array.prototype.slice.call(
      this.sortedGEMS); // Do not mutate original elms;
      this.sortedGEMS = gemsList.sort(
        compare(field, null, this.sortAsc ? 'asc' : 'desc'));
      this.sortAsc = !this.sortAsc;
    },
    toggleMaintainedModels() {
      this.showMaintained = !this.showMaintained;
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

#models {
  .title {
    display: block;
    margin-bottom: 1rem;
  }

  th {
    cursor: pointer;
  }

  #show-m-but {
    margin-bottom: 1rem;
    &.is-active {
      border: 1px solid #505050;
    }
  }

  .dsc, .name {
    height: 75px;
    line-height: 75px;

    span {
      display: inline-block;
      vertical-align: middle;
      line-height: normal;
    }
  }

  .m-row {
    cursor: pointer;
  }

  .name {
    font-size: 1.5rem;
  }

  .modal-content {
    width: 1024px;
    padding: 1rem;
    background: white;
  }
}

</style>
