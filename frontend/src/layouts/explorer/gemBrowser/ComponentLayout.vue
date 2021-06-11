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
          <div class="column is-9-widescreen is-9-desktop is-full-tablet">
            <div class="table-container">
              <slot name="table" />
            </div>
            <ExtIdTable :type="componentType" :external-dbs="externalDbs"></ExtIdTable>
          </div>
          <div class="column is-3-widescreen is-3-desktop is-half-tablet has-text-centered">
            <router-link v-if="interactionPartnerId" class="button is-info is-fullwidth is-outlined"
                            :to="{
                            name: 'interaction',
                            params: { model: interactionPartnerModel, id: interactionPartnerId }
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
        :selected-elm-id="selectedElmId" :related-met-count="relatedMetCount"/>
      </div>
    </div>
  </div>
</template>


<script>

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
    interactionPartnerId: { type: String, default: '' },
    interactionPartnerModel: { type: String, default: '' },
    viewerSelectedID: { type: String, default: '' },
    selectedElmId: { type: String, required: false, default: null },
    relatedMetCount: { type: Number, required: false, default: 0 },
  },
  data() {
    return {
      componentId: this.$route.params.id,
      modelNotFound: false,
      componentNotFound: false,
      showLoaderMessage: '',
      messages,
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
        this.showLoaderMessage = '';
      } catch {
        this.componentNotFound = true;
      }
    },
  },
};
</script>

<style lang="scss"></style>
