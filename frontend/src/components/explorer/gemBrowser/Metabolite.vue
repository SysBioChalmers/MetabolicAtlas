<template>
  <div class="section extended-section">
    <div class="container is-fullhd">
      <div v-if="modelErrorMessage" class="columns is-centered">
        <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
          {{ modelErrorMessage }}
        </div>
      </div>
      <div v-if="componentNotFound" class="columns is-centered">
        <notFound :type="type" :component-id="metaboliteId"></notFound>
      </div>
      <div v-else>
        <div class="columns">
          <div class="column">
            <h3 class="title is-3">
              <span class="is-capitalized">{{ type }}</span> {{ metabolite.name }}
              <span v-if="metabolite && metabolite.compartment" class="has-text-weight-light has-text-grey-light">
                in {{ metabolite.compartment.name }}
              </span>
            </h3>
          </div>
        </div>
        <loader v-if="showLoaderMessage" :message="showLoaderMessage" class="columns" />
        <template v-else>
          <div class="columns is-multiline metabolite-table is-variable is-8">
            <div class="column is-7-widescreen is-7-desktop is-full-tablet">
              <div class="table-container">
                <table v-if="metabolite" class="table main-table is-fullwidth">
                  <tr v-for="el in mainTableKey" :key="el.name">
                    <td v-if="el.display"
                        class="td-key has-background-primary has-text-white-bis" v-html="el.display">
                    </td>
                    <td v-else-if="el.name === 'id'"
                        class="td-key has-background-primary has-text-white-bis">
                      {{ model ? model.short_name : '' }} ID
                    </td>
                    <td v-else class="td-key has-background-primary has-text-white-bis">
                      {{ reformatTableKey(el.name) }}
                    </td>
                    <td v-if="metabolite[el.name] !== null">
                      <span v-if="el.name === 'formula'"
                            v-html="chemicalFormula(metabolite[el.name], metabolite.charge)">
                      </span>
                      <span v-else-if="el.modifier" v-html="el.modifier(metabolite[el.name])">
                      </span>
                      <span v-else-if="el.name === 'compartment' && metabolite[el.name]">
                        <!-- eslint-disable-next-line max-len -->
                        <router-link :to="{ name: 'compartment', params: { model: model.short_name, id: metabolite[el.name].id } }"
                        >{{ metabolite[el.name].id }}</router-link>
                      </span>
                      <span v-else>
                        {{ metabolite[el.name] }}
                      </span>
                    </td>
                    <td v-else> - </td>
                  </tr>
                  <tr v-if="relatedMetabolites.length !== 0">
                    <td class="td-key has-background-primary has-text-white-bis">Related metabolite(s)</td>
                    <td>
                      <span v-for="(rm, i) in relatedMetabolites" :key="rm.id">
                        <br v-if="i !== 0">
                        <!-- eslint-disable-next-line max-len -->
                        <router-link :to="{ name: 'metabolite', params: { model: model.short_name, id: rm.id } }">
                          {{ rm.fullName }}
                        </router-link> in {{ rm.compartment.name }}
                      </span>
                    </td>
                  </tr>
                </table>
              </div>
              <ExtIdTable :type="type" :external-dbs="metabolite.externalDbs"></ExtIdTable>
            </div>
            <div v-if="metabolite && metabolite.externalDbs && metabolite.externalDbs.ChEBI"
                 class="column is-3-widescreen is-2-desktop is-full-tablet has-text-centered px-2">
              <a :href="metabolite.externalDbs.ChEBI[0].url" target="_blank">
                <img :src="`https://www.ebi.ac.uk/chebi/displayImage.do?defaultImage=true&imageIndex=0&chebiId=${metabolite.externalDbs.ChEBI[0].id.slice(6)}&dimensions=400`" />
              </a>
            </div>
            <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
              <router-link v-if="model" class="button is-info is-fullwidth is-outlined"
                           :to="{ name: 'interaction',
                                  params: { model: model.short_name, id: metaboliteId } }">
                <span class="icon"><i class="fa fa-connectdevelop fa-lg"></i></span>&nbsp;
                <span>{{ messages.interPartName }}</span>
              </router-link>
              <br>
              <!-- eslint-disable-next-line max-len -->
              <maps-available :id="metaboliteId" :type="type" :viewer-selected-i-d="metabolite.id" />
              <gem-contact :id="metaboliteId" :type="type" />
            </div>
          </div>
          <reaction-table :selected-elm-id="metaboliteId" :source-name="metaboliteId" :type="type"
                          :related-met-count="relatedMetabolites.length" />
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import MapsAvailable from '@/components/explorer/gemBrowser/MapsAvailable';
import ReactionTable from '@/components/explorer/gemBrowser/ReactionTable';
import GemContact from '@/components/shared/GemContact';
import NotFound from '@/components/NotFound';
import Loader from '@/components/Loader';
import ExtIdTable from '@/components/explorer/gemBrowser/ExtIdTable';
import { chemicalFormula } from '@/helpers/chemical-formatters';
import { reformatTableKey } from '@/helpers/utils';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'Metabolite',
  components: {
    NotFound,
    Loader,
    ExtIdTable,
    MapsAvailable,
    ReactionTable,
    GemContact,
  },
  data() {
    return {
      type: 'metabolite',
      metaboliteId: this.$route.params.id,
      mainTableKey: [
        { name: 'id' },
        { name: 'name' },
        { name: 'alternateName', display: 'Alternate name' },
        { name: 'synonyms' },
        { name: 'description' },
        { name: 'formula' },
        { name: 'charge' },
        { name: 'inchi', display: 'InChI' },
        { name: 'compartment' },
      ],
      activePanel: 'table',
      componentNotFound: false,
      showLoaderMessage: '',
      modelErrorMessage: '',
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      metabolite: state => state.metabolites.metabolite,
      relatedMetabolites: state => state.metabolites.relatedMetabolites,
    }),
  },
  watch: {
    '$route.params': 'setup',
  },
  async created() {
    if (!this.model || this.model.short_name !== this.$route.params.model) {
      const modelSelectionSuccessful = await this.$store.dispatch('models/selectModel', this.$route.params.model);
      if (!modelSelectionSuccessful) {
        this.modelErrorMessage = `Error: ${messages.modelNotFound}`;
      }
    }
    this.setup();
  },
  methods: {
    async setup() {
      this.showLoaderMessage = 'Loading metabolite data';
      try {
        const payload = { model: this.model, id: this.metaboliteId };
        await this.$store.dispatch('metabolites/getMetaboliteData', payload);
        this.componentNotFound = false;
        this.showLoaderMessage = '';
        await this.getRelatedMetabolites();
      } catch {
        this.componentNotFound = true;
        document.getElementById('search').focus();
      }
    },
    async getRelatedMetabolites() {
      try {
        const payload = { model: this.model, id: this.metaboliteId };
        await this.$store.dispatch('metabolites/getRelatedMetabolites', payload);
      } catch {
        this.$store.dispatch('metabolites/clearRelatedMetabolites');
      }
    },
    reformatTableKey(k) { return reformatTableKey(k); },
    chemicalFormula,
  },
};
</script>

<style lang="scss"></style>
