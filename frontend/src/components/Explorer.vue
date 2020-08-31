<template>
  <section :class="{ 'section extended-section' : !extendWindow }">
    <div :class="{ 'container is-fullhd': !extendWindow }">
      <template v-if="modelNotFound">
        <div class="columns is-centered">
          <notFound type="model" :component-id="modelNotFound"></notFound>
        </div>
      </template>
      <template v-else-if="currentShowComponent">
        <keep-alive>
          <component :is="currentShowComponent" />
        </keep-alive>
      </template>
      <template v-else>
        <div class="columns has-text-centered">
          <div class="column">
            <h3 class="title is-size-3">Explore the integrated models</h3>
          </div>
        </div>
        <br>
        <div class="columns">
          <div class="column has-text-centered">
            <p class="has-text-weight-bold is-size-5">1. Select a model:</p>
          </div>
        </div>
        <div v-if="model" class="columns is-multiline is-centered">
          <div v-for="cmodel in Object.values(models).sort((a, b) =>
                 (a.short_name.toLowerCase() < b.short_name.toLowerCase() ? -1 : 1))"
               :key="cmodel.short_name" class="column is-5-desktop is-half-tablet">
            <div id="selectedModel" style="height: 100%"
                 class="box has-text-centered clickable hoverable"
                 :class="cmodel.short_name === model.short_name ? 'selectedBox' : ''"
                 :title="`Select ${cmodel.short_name} as the model to explore`"
                 @mousedown.prevent="selectModel(cmodel)">
              <p class="title is-5"
                 :class="cmodel.short_name === model.short_name ? 'has-text-primary' : ''">
                <span v-if="cmodel.short_name === model.short_name"
                      class="icon"><i class="fa fa-check-square-o"></i></span>
                <span v-else><i class="fa fa-square-o">&nbsp;</i></span>
                &nbsp;{{ cmodel.short_name }} {{ cmodel.version }}
              </p>
              <p>{{ cmodel.full_name }}</p>
              <p class="has-text-grey is-touch-hidden">
                {{ cmodel.reaction_count }} reactions -
                {{ cmodel.metabolite_count }} metabolites -
                {{ cmodel.gene_count }} genes
              </p>
            </div>
          </div>
        </div>
        <br><br><br>
        <div class="columns">
          <div class="column has-text-centered">
            <p class="has-text-weight-bold is-size-5">2. Select a tool:</p>
          </div>
        </div>
        <div v-if="model" class="columns is-multiline is-centered">
          <div v-for="tool in explorerTools" :key="tool.name"
               class="column is-one-fifth-widescreen is-4-desktop is-4-tablet">
            <router-link :to="{ name: tool.routeName, params: { model: model.short_name } }"
                         :title="`Click to access the ${tool.name} for ${model.short_name}`">
              <div class="card card-fullheight hoverable">
                <header class="card-header">
                  <p class="card-header-title is-block has-text-centered is-size-5">
                    <span class="icon is-medium" style="width: 100%">
                      <i :class="`fa fa-${tool.icon}`"></i>
                      &nbsp;&nbsp;{{ tool.name }}
                    </span>
                    <span class="is-visible-desktop has-text-grey-light" style="width: 100%">
                      {{ model.short_name }}
                    </span>
                  </p>
                </header>
                <div class="card-content">
                  <div class="content">
                    <img :src="tool.img" />
                  </div>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import GemBrowser from '@/components/explorer/GemBrowser';
import MapViewer from '@/components/explorer/MapViewer';
import InteractionPartners from '@/components/explorer/InteractionPartners';
import ThreeDviewer from '@/components/explorer/ThreeDviewer';
import NotFound from '@/components/NotFound';
import { default as messages } from '@/helpers/messages';
import { default as EventBus } from '../event-bus';

export default {
  name: 'Explorer',
  components: {
    GemBrowser,
    MapViewer,
    InteractionPartners,
    ThreeDviewer,
    NotFound,
  },
  data() {
    return {
      /* eslint-disable global-require */
      explorerTools: [
        { name: messages.gemBrowserName,
          img: require('../assets/gemBrowser.jpg'),
          routeName: 'browserRoot',
          icon: 'table' },
        { name: messages.mapViewerName,
          img: require('../assets/mapViewer.jpg'),
          routeName: 'viewerRoot',
          icon: 'map-o' },
        { name: messages.interPartName,
          img: require('../assets/interaction.jpg'),
          routeName: 'interPartnerRoot',
          icon: 'share-alt' },
        { name: 'New 3D Viewer',
          img: '',
          routeName: 'threeDviewerRoot',
          icon: 'spinner' },
      ],
      modelNotFound: null,
      extendWindow: false,
      currentShowComponent: '',

      compartments: {},
      errorMessage: '',
    };
  },
  computed: {
    ...mapGetters({
      models: 'models/models',
    }),
    ...mapState({
      model: state => state.models.model,
    }),
  },
  watch: {
    /* eslint-disable-next-line quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  async created() {
    await this.getModelList();
  },
  methods: {
    setup() {
      if (!this.model) {
        // do not redirect on url change unless the model is already loaded
        return;
      }
      if (this.$route.params.model) {
        if (this.$route.params.model in this.models) {
          this.selectModel(this.models[this.$route.params.model]);
        } else {
          this.modelNotFound = this.$route.params.model;
          return;
        }
      } else if (this.$route.query.selected && this.$route.query.selected in this.models) {
        this.selectModel(this.models[this.$route.query.selected]);
      } else {
        this.selectModel(this.model);
      }

      this.modelNotFound = null;
      if (['viewerRoot', 'viewer'].includes(this.$route.name)) {
        this.displayViewer();
      } else if (['browserRoot', 'browser'].includes(this.$route.name)) {
        this.displayBrowser();
      } else if (['interPartnerRoot', 'interPartner'].includes(this.$route.name)) {
        this.displayInterPartner();
      } else if (['threeDviewerRoot'].includes(this.$route.name)) {
        this.displayThreeDViewer();
      } else {
        EventBus.$emit('destroy3Dnetwork');
        this.extendWindow = false;
        this.currentShowComponent = '';
      }
    },
    async getModelList() {
      // get integrated models list
      try {
        await this.$store.dispatch('models/getModels');

        const defaultModelKey = Object.keys(this.models).sort(
          (a, b) => (a.toLowerCase() < b.toLowerCase() ? -1 : 1))[0];
        let defaultModel = this.models[defaultModelKey];
        if (this.$route.params.model && this.$route.params.model in this.models) {
          // if a model DB is provide in the URL, use it to select the model
          defaultModel = this.models[this.$route.params.model];
        } else if (this.$route.name === 'explorerRoot' && this.$route.query && this.$route.query.selected) {
          // or if a selected=NAME is provided in the URL, try to use it to select the model
          const modelShortNamesDict = {};
          Object.values(this.models).forEach((m) => { modelShortNamesDict[m.short_name] = m; });
          if (this.$route.query.selected in modelShortNamesDict) {
            defaultModel = modelShortNamesDict[this.$route.query.selected];
          }
        }
        this.$store.dispatch('models/selectModel', defaultModel);
        this.setup();
      } catch {
        this.errorMessage = messages.unknownError;
      }
    },
    selectModel(model) {
      if (!this.model || model.short_name !== this.model.short_name) {
        this.$store.dispatch('models/selectModel', model);
      }
      if (this.$route.name === 'explorerRoot'
         && (!this.$route.query || !this.$route.query.selected
          || this.$route.query.selected !== this.model.short_name)) {
        this.$router.replace({ name: 'explorerRoot', query: { selected: this.model.short_name } }).catch(() => {});
      }
    },
    displayBrowser() {
      this.extendWindow = false;
      this.currentShowComponent = 'GemBrowser';
    },
    displayViewer() {
      this.extendWindow = true;
      this.currentShowComponent = 'MapViewer';
    },
    displayInterPartner() {
      this.extendWindow = false;
      this.currentShowComponent = 'InteractionPartners';
    },
    displayThreeDViewer() {
      this.extendWindow = true;
      this.currentShowComponent = 'threeDviewer';
    },
  },
};

</script>

<style lang="scss">

#selectedModel.selectedBox {
  box-shadow: $shadow-primary-light;
}

</style>
