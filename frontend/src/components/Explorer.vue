<template>
  <section class="section extended-section">
    <div class="container is-fullhd">
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
      <div v-if="model" class="columns is-multiline is-centered is-variable is-4">
        <div v-for="cmodel in Object.values(models).sort((a, b) =>
               (a.short_name.toLowerCase() < b.short_name.toLowerCase() ? -1 : 1))"
             :key="cmodel.short_name" class="column is-4-desktop is-half-tablet">
          <div id="selectedModel" style="height: 100%"
               class="box has-text-centered is-clickable hoverable"
               :class="cmodel.short_name === model.short_name ? 'selectedBox' : ''"
               :title="`Select ${cmodel.short_name} as the model to explore`"
               @mousedown.prevent="selectModel(cmodel.short_name)">
            <p class="title is-5"
               :class="cmodel.short_name === model.short_name ? 'has-text-primary' : ''">
              <span v-if="cmodel.short_name === model.short_name"
                    class="icon"><i class="fa fa-check-square-o"></i></span>
              <span v-else><i class="fa fa-square-o">&nbsp;</i></span>
              &nbsp;{{ cmodel.short_name }} {{ cmodel.version }}
            </p>
            <p class="subtitle is-italic">
              {{ cmodel.full_name.split(" ").splice(-2).join(" ") }}
            </p>
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
      <div v-if="model" class="columns is-multiline is-centered is-variable is-4">
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
              <div class="card-content py-2">
                <div class="content">
                  <img :src="tool.img" />
                </div>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'Explorer',
  data() {
    return {
      /* eslint-disable global-require */
      explorerTools: [
        { name: messages.gemBrowserName,
          img: require('../assets/gemBrowser.jpg'),
          routeName: 'browser',
          icon: 'table' },
        { name: messages.mapViewerName,
          img: require('../assets/mapViewer.jpg'),
          routeName: 'viewer',
          icon: 'map-o' },
        { name: messages.interPartName,
          img: require('../assets/interaction.jpg'),
          routeName: 'interaction',
          icon: 'share-alt' },
      ],
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
  mounted() {
    const modelShortName = this.$route.params.model;
    if (modelShortName && this.model) {
      this.selectModel(modelShortName);
    }
  },
  methods: {
    selectModel(modelShortName) {
      if (modelShortName !== this.$route.params.model) {
        this.$router.replace({ params: { model: modelShortName } });
      }
      if (modelShortName !== this.model.short_name) {
        this.$store.dispatch('models/selectModel', modelShortName);
      }
    },
  },
};

</script>

<style lang="scss">

#selectedModel.selectedBox {
  box-shadow: $shadow-primary-light;
}

</style>
