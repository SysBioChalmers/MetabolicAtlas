<template>
  <div class="section extended-section">
    <div class="container is-fullhd">
      <div v-if="modelNotFound || componentNotFound" class="columns is-centered">
        <NotFound
          :type="modelNotFound ? 'model' : type"
          :component-id="modelNotFound ? $route.params.model : geneId" />
      </div>
      <div v-else>
        <div class="container is-fullhd columns">
          <div class="column">
            <h3 class="title is-3">
              <span class="is-capitalized">{{ type }}</span> {{ gene.geneName }}
            </h3>
          </div>
        </div>
        <loader v-if="showLoaderMessage" :message="showLoaderMessage" class="columns" />
        <div v-else class="columns">
          <div class="column">
            <div class="columns is-multiline is-variable is-8">
              <div id="gene-details" class="reaction-table column">
                <div class="table-contaner">
                  <table v-if="gene && Object.keys(gene).length !== 0" class="table main-table is-fullwidth">
                    <tr v-for="el in mainTableKey" :key="el.name">
                      <td v-if="'display' in el"
                          class="td-key has-background-primary has-text-white-bis"
                          v-html="el.display"></td>
                      <td v-else-if="el.name === 'id'"
                          class="td-key has-background-primary has-text-white-bis">
                        {{ model? model.short_name : '' }} ID
                      </td>
                      <td v-else
                          class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                      <td v-if="gene[el.name]">
                        <span v-if="'modifier' in el" v-html="el.modifier(gene)">
                        </span>
                        <span v-else>
                          {{ gene[el.name] }}
                        </span>
                      </td>
                      <td v-else> - </td>
                    </tr>
                  </table>
                </div>
                <ExtIdTable :type="type" :external-dbs="gene.externalDbs"></ExtIdTable>
              </div>
              <div class="column is-narrow">
                <router-link v-if="model && gene.id" class="button is-info is-fullwidth is-outlined"
                             :to="{ name: 'interaction', params: { model: model.short_name, id: gene.id } }">
                  <span class="icon"><i class="fa fa-connectdevelop fa-lg"></i></span>&nbsp;
                  <span>{{ messages.interPartName }}</span>
                </router-link>
                <br>
                <maps-available :id="geneId" :type="type" :viewer-selected-i-d="gene.id" />
                <gem-contact :id="geneId" :type="type" />
              </div>
            </div>
            <reaction-table v-if="model && geneName" :source-name="geneName" :type="type" :selected-elm-id="geneName" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import NotFound from '@/components/NotFound';
import Loader from '@/components/Loader';
import ExtIdTable from '@/components/explorer/gemBrowser/ExtIdTable';
import MapsAvailable from '@/components/explorer/gemBrowser/MapsAvailable';
import ReactionTable from '@/components/explorer/gemBrowser/ReactionTable';
import GemContact from '@/components/shared/GemContact';
import { reformatTableKey } from '@/helpers/utils';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'Gene',
  components: {
    NotFound,
    Loader,
    MapsAvailable,
    ReactionTable,
    GemContact,
    ExtIdTable,
  },
  data() {
    return {
      showReactionLoader: true,
      geneId: '',
      type: 'gene',
      mainTableKey: [
        { name: 'id' },
        { name: 'name', display: 'Gene&nbsp;name' },
        { name: 'alternateName', display: 'Alternate&nbsp;name' },
        { name: 'synonyms' },
        { name: 'function' },
      ],
      limitReaction: 200,
      componentNotFound: false,
      showLoaderMessage: '',
      modelNotFound: false,
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      gene: state => state.genes.gene,
    }),
    ...mapGetters({
      geneName: 'genes/geneName',
    }),
  },
  watch: {
    '$route.params': 'setup',
  },
  async created() {
    if (!this.model || this.model.short_name !== this.$route.params.model) {
      const modelSelectionSuccessful = await this.$store.dispatch('models/selectModel', this.$route.params.model);
      if (!modelSelectionSuccessful) {
        this.modelNotFound = true;
      }
    }
    this.setup();
  },
  methods: {
    async setup() {
      this.showLoaderMessage = 'Loading gene data';
      this.geneId = this.$route.params.id;
      try {
        const payload = { model: this.model, id: this.geneId };
        await this.$store.dispatch('genes/getGeneData', payload);
        this.componentNotFound = false;
        this.showLoaderMessage = '';
      } catch {
        this.reactions = [];
        this.componentNotFound = true;
      }
    },
    reformatTableKey(k) { return reformatTableKey(k); },
  },
};

</script>

<style lang="scss">
</style>
