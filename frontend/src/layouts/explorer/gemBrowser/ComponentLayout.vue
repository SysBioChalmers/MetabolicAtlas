<template>
  <div class="section extended-section">
    <div class="container is-fullhd">
      <div v-if="modelNotFound || componentNotFound" class="columns is-centered">
        <NotFound
          :type="modelNotFound ? 'model' : componentType"
          :component-id="modelNotFound ? $route.params.model : componentId" />
      </div>
      <div v-else>
        <div class="columns">
          <div class="column">
            <h3 class="title is-3">
              <span class="is-capitalized">{{ componentType }}</span> {{ componentName }}
            </h3>
          </div>
        </div>
        <loader v-if="showLoaderMessage" :message="showLoaderMessage" class="columns" />
        <div v-else class="columns is-multiline is-variable is-8">
          <div class="gembrowser-table column">
            <div class="table-container">
              <slot name="table" />
            </div>
            <ExtIdTable :type="componentType" :external-dbs="externalDbs"></ExtIdTable>
          </div>
          <div v-if="chebiImageLink"
                 class="column is-3-widescreen is-2-desktop is-full-tablet has-text-centered px-2">
              <a :href="chebi.url" target="_blank">
                <img id="chebi-img" :src="chebiImageLink" class="hoverable" />
                <a :href="chebi.url" target="_blank" style="display: block;">
                  {{ componentName }} via ChEBI</a>
              </a>
            </div>
          <div class="column is-3-widescreen is-3-desktop is-half-tablet has-text-centered">
            <router-link v-if="interactionPartner" class="button is-info is-fullwidth is-outlined"
                            :to="{
                            name: 'interaction',
                            params: { model: model.short_name, id: componentId }
                            }">
                <span class="icon"><i class="fa fa-connectdevelop fa-lg"></i></span>&nbsp;
                <span>{{ messages.interPartName }}</span>
            </router-link>
            <br>
            <maps-available :id="componentId" :type="componentType"
            :viewer-selected-i-d="viewerSelectedID"></maps-available>
            <gem-contact :id="componentId" :type="componentType" />
          </div>
        </div>
        <reaction-table v-if="model && includeReactionTable" :source-name="componentId" :type="componentType"
        :selected-elm-id="selectedElm ? componentId : null" :related-met-count="relatedMetCount"/>
      </div>
    </div>
  </div>
</template>


<script>
import axios from 'axios';
import { mapState } from 'vuex';
import NotFound from '@/components/NotFound';
import Loader from '@/components/Loader';
import MapsAvailable from '@/components/explorer/gemBrowser/MapsAvailable';
import ExtIdTable from '@/components/explorer/gemBrowser/ExtIdTable';
import ReactionTable from '@/components/explorer/gemBrowser/ReactionTable';
import GemContact from '@/components/shared/GemContact';
import { default as messages } from '@/helpers/messages';

export default {
  components: {
    NotFound,
    Loader,
    MapsAvailable,
    ReactionTable,
    ExtIdTable,
    GemContact,
  },
  props: {
    componentType: { type: String },
    componentName: { type: String },
    externalDbs: { type: Object, default: () => {} },
    queryComponentAction: { type: String },
    includeReactionTable: { type: Boolean, default: true },
    interactionPartner: { type: Boolean, default: false },
    viewerSelectedID: { type: String, default: '' },
    selectedElm: { type: Boolean, required: false, default: true },
    relatedMetCount: { type: Number, required: false, default: 0 },
    chebi: { type: Object, required: false, default: null },

  },
  data() {
    return {
      componentId: this.$route.params.id,
      modelNotFound: false,
      componentNotFound: false,
      showLoaderMessage: '',
      messages,
      chebiImageLink: null,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
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

    await this.setup();
  },
  methods: {
    async setup() {
      this.componentId = this.$route.params.id;
      this.showLoaderMessage = `Loading ${this.queryComponentAction.replace('compartmentalized', '').toLowerCase()} data`;

      try {
        const payload = { model: this.model, id: this.componentId };
        await this.$store.dispatch(this.queryComponentAction, payload);
        this.componentNotFound = false;
        if (this.chebi) {
          const link = `https://www.ebi.ac.uk/chebi/displayImage.do?defaultImage=true&imageIndex=0&chebiId=${this.chebi.id.slice(6)}`;
          const { data } = await axios.get(link);
          if (data !== '') {
            this.chebiImageLink = `${link}&dimensions=400`;
          }
        }
        this.showLoaderMessage = '';
      } catch {
        this.componentNotFound = true;
      }
    },
  },
};
</script>

<style lang="scss"></style>
