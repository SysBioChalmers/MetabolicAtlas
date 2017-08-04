<template>
   <div v-if="errorMessage">
    {{ errorMessage }}
   </div>
  <div v-else>
    <span class="title">Models</span>
    <br>
    <span id="show-m-but" class="button is-primary" :class="{'is-active': showMaintained }"
    @click="showMaintained = !showMaintained">
      Maintained only
    </span>
    <div class="container">
      <table v-show="filteredOldGEMS.length != 0" 
      class="table is-bordered is-striped is-narrow">
        <thead>
          <tr>
            <th v-for="f in fields"
              @click="sortBy(f.name)">{{ f.display }}
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
     <div class="modal" v-bind:class="{ 'is-active': showModelTable }">
      <div class="modal-background" @click="showModelTable = false"></div>
      <div class="modal-content">
        <div id="modal-info">
        <span class="title is is-primary">Model {{ selectedModel.label }}</span>
          <table class="table">
            <tbody>
              <tr v-for="field in model_fields">
                <td v-html="field.display "></td>
                <td v-if="typeof(selectedModel[field.name]) === 'boolean'">
                  {{ selectedModel[field.name] ? 'yes' : 'No' }}
                </td>
                <td v-else>
                  {{ selectedModel[field.name] }}
                </td>
              </tr>
              <tr>
                <td>Reference</td>
                <td v-if="selectedModel.link">
                  <a :href="selectedModel.link" target="_blank">
                    {{ selectedModel.title }}
                  </a>
                </td>
                <td v-else>
                    {{ selectedModel.title }}
                </td>
              </tr>
              <tr>
                <td>PUMED ID</td>
                <td>
                  <a :href="'https://www.ncbi.nlm.nih.gov/pubmed/' + selectedModel.pubmed" 
                  target="_blank">
                    {{ selectedModel.pubmed }}
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
          <br>
          <span class="subtitle">Files</span>
          <table class="table">
            <thead>
              <tr>
                <th v-for="file in selectedModel.files">{{ file.format }}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td v-for="file in selectedModel.files">
                  <a href="">{{ file.path }}</a>
                </td>
              </tr>
            </tbody>
          </table>
        </div> 
      </div> 
      <button class="modal-close" @click="showModelTable = false"></button>
    </div>
  </div>
</template>


<script>
import axios from 'axios';
import $ from 'jquery';
import { default as compare } from '../helpers/compare';

export default {
  name: 'resources',
  data() {
    return {
      fields: [
        { name: 'organism', display: 'Organism' },
        { name: 'set_name', display: 'Set' },
        { name: 'label', display: 'Label' },
        { name: 'organ_system', display: 'System' },
        { name: 'tissue', display: 'Tissue' },
        { name: 'cell_type', display: 'Cell type' },
        { name: 'reaction_count', display: '# reactions' },
        { name: 'metabolite_count', display: '# metabolites' },
        { name: 'enzyme_count', display: '# enzymes' },
        { name: 'year', display: 'Year' },
        { name: 'maintained', display: 'Maintained' },
      ],
      model_fields: [
        { name: 'description', display: 'Description' },
        { name: 'organism', display: 'Organism' },
        { name: 'set_name', display: 'Set' },
        { name: 'organ_system', display: 'System' },
        { name: 'tissue', display: 'Tissue' },
        { name: 'cell_type', display: 'Cell type' },
        { name: 'reaction_count', display: '#&nbsp;reactions' },
        { name: 'metabolite_count', display: '#&nbsp;metabolites' },
        { name: 'enzyme_count', display: '#&nbsp;enzymes' },
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
    };
  },
  computed: {
    filteredOldGEMS: function f() {
      return this.showMaintained ?
       this.sortedGEMS.filter(el => el.maintained) : this.sortedGEMS;
    },
  },
  methods: {
    getModel(id) {
      console.log(id);
      axios.get(`gemodel/${id}`)
      .then((response) => {
        console.log(response);
        let model = response.data;
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
        model = $.extend(model, model.reference);
        delete model.reference;
        if (!model.description) {
          model.description = setDescription;
        }

        this.selectedModel = model;
        console.log(this.selectedModel);
        this.showModelTable = true;
      })
      .catch(() => {
        this.showModelTable = false;
      });
    },
    getModels() {
      axios.get('gemodels/')
      .then((response) => {
        this.GEMS = [];
        console.log(response.data);
        for (let i = 0; i < response.data.length; i += 1) {
          const gem = response.data[i];
          const sample = gem.sample;
          delete gem.sample;
          this.GEMS.push($.extend(gem, sample));
        }
        this.sortedGEMS = this.GEMS;
        this.errorMessage = '';
      })
      .catch((error) => {
        console.log(error);
        this.errorMessage = this.$t('notFoundError');
      });
    },
    sortBy(field) {
      const gemsList = Array.prototype.slice.call(
      this.sortedGEMS); // Do not mutate original elms;
      this.sortedGEMS = gemsList.sort(
        compare(field, this.sortAsc ? 'asc' : 'desc'));
      this.sortAsc = !this.sortAsc;
    },
  },
  beforeMount() {
    this.getModels();
  },
};

</script>

<style lang="scss">

.title {
  display: block;
  margin-bottom: 1rem;
}

#show-m-but {
  margin-bottom: 1rem;
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

</style>
