<template>
  <div id="metabolite-page">
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
          <div class="column is-10-widescreen is-9-desktop is-full-tablet">
            <div class="table-container">
              <table v-if="metabolite" class="table main-table is-fullwidth">
                <tr v-for="el in mainTableKey" :key="el.name">
                  <td v-if="el.display"
                      class="td-key has-background-primary has-text-white-bis" v-html="el.display">
                  </td>
                  <td v-else-if="el.name === 'id'"
                      class="td-key has-background-primary has-text-white-bis">
                    {{ model.short_name }} ID
                  </td>
                  <td v-else class="td-key has-background-primary has-text-white-bis">
                    {{ reformatTableKey(el.name) }}
                  </td>
                  <td v-if="metabolite[el.name] !== null">
                    <span v-if="el.name === 'formula'" v-html="chemicalFormula(metabolite[el.name], metabolite.charge)">
                    </span>
                    <span v-else-if="el.modifier" v-html="el.modifier(metabolite[el.name])">
                    </span>
                    <span v-else-if="el.name === 'compartment' && metabolite[el.name]">
                      <!-- eslint-disable-next-line max-len -->
                      <router-link :to="{ name: 'browser', params: { model: model.short_name, type: 'compartment', id: metabolite[el.name].id } }"
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
                      <router-link :to="{ name: 'browser', params: { model: model.short_name, type: 'metabolite', id: rm.id } }">
                        {{ rm.fullName }}
                      </router-link> in {{ rm.compartment.name }}
                    </span>
                  </td>
                </tr>
              </table>
            </div>
            <ExtIdTable :type="type" :external-dbs="metabolite.externalDbs"></ExtIdTable>
          </div>
          <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
            <router-link class="button is-info is-fullwidth is-outlined"
                         :to="{ name: 'interPartner', params: { model: model.short_name, id: metaboliteId } }">
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
      messages,
      type: 'metabolite',
      metaboliteId: '',
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
    $route() {
      this.setup();
    },
  },
  beforeMount() {
    this.setup();
  },
  methods: {
    async setup() {
      this.showLoaderMessage = 'Loading metabolite data';
      this.metaboliteId = this.$route.params.id;
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
