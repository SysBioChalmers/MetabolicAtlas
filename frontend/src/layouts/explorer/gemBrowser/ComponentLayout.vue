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
              <span v-if="compartmentName" class="has-text-weight-light has-text-grey-light">
                in {{ compartmentName }} </span>
            </h3>
          </div>
        </div>
        <loader v-if="showLoaderMessage" :message="showLoaderMessage" class="columns" />
        <div v-else class="columns is-multiline is-variable is-8 is-centered">
          <div class="table-template column">
            <div class="table-container">
              <slot name="table" />
            </div>
            <ExtIdTable v-if="externalDbs" :type="componentType" :external-dbs="externalDbs"></ExtIdTable>
            <p v-if="model && !externalDbs">The
              <a :href="`/api/v2/${model.apiVersion}/compartments/${componentId}?full=true`"
                 target="_blank">complete list in JSON format</a>
              of reactions / metabolites / genes is available using our
              <a href="/api/v2" target="_blank">API</a></p>
          </div>
          <slot v-if="isMetabolite" name="chebi" />
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
        <references v-if="referenceList && !showLoaderMessage" :reference-list="referenceList" />
        <reaction-table v-if="model && includeReactionTable" :source-name="componentId" :type="componentType"
                        :selected-elm-id="selectedElmId ? componentId : null" :related-met-count="relatedMetCount" />
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
import References from '@/components/shared/References';
import { default as messages } from '@/helpers/messages';

export default {
  components: {
    NotFound,
    Loader,
    MapsAvailable,
    ReactionTable,
    ExtIdTable,
    GemContact,
    References,
  },
  props: {
    componentType: { type: String },
    componentName: { type: String },
    compartmentName: { type: String, default: '' },
    externalDbs: { type: Object, default: null },
    queryComponentAction: { type: String },
    includeReactionTable: { type: Boolean, default: true },
    interactionPartner: { type: Boolean, default: false },
    viewerSelectedID: { type: String, default: '' },
    selectedElmId: { type: Boolean, required: false, default: false },
    relatedMetCount: { type: Number, required: false, default: 0 },
    isMetabolite: { type: Boolean, default: false },
    referenceList: { type: Object, default: null },
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
        if (this.$listeners && this.$listeners.handleCallback) {
          this.$emit('handleCallback');
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
