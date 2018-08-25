<template>
  <div>
    <div class="columns" v-if="!selectedType">
      <div class="column container has-text-centered">
        <h4 class="title is-4">Explore through {{ $t(model) }} with the Gems Browser</h4>
      </div>
    </div>
    <div class="columns">
      <div class="column is-3">
      </div>
      <global-search
      :quickSearch=true
      :model="model"
      ref="globalSearch"></global-search>
    </div>
    <div v-if="errorMessage">
      {{ errorMessage }}
    </div>
    <div v-else>
      <closest-interaction-partners v-if="selectedType==='interaction'" :model="model"></closest-interaction-partners>
      <enzyme v-if="selectedType==='enzyme'" :model="model"></enzyme>
      <metabolite v-if="selectedType==='metabolite'" :model="model"></metabolite>
      <reaction v-if="selectedType==='reaction'" :model="model"></reaction>
      <subsystem v-if="selectedType==='subsystem'" :model="model"></subsystem>
    </div>
  </div>
</template>

<script>
import GlobalSearch from 'components/explorer/GlobalSearch';
import ClosestInteractionPartners from 'components/explorer/gemsBrowser/ClosestInteractionPartners';
import Enzyme from 'components/explorer/gemsBrowser/Enzyme';
import Metabolite from 'components/explorer/gemsBrowser/Metabolite';
import Reaction from 'components/explorer/gemsBrowser/Reaction';
import Subsystem from 'components/explorer/gemsBrowser/Subsystem';
import { default as EventBus } from '../../event-bus';


export default {
  name: 'gems-browser',
  components: {
    ClosestInteractionPartners,
    Enzyme,
    Metabolite,
    Reaction,
    Subsystem,
    GlobalSearch,
  },
  props: ['model'],
  data() {
    return {
      selectedType: '',
      searchTerm: '',
      searchResults: [],
      errorMessage: '',
      componentID: '',
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  beforeMount() {
    this.dBImageSources = require.context('../../assets', false, /\.(png|gif|jpg)$/);
    this.setup();
  },
  created() {
    // init the global events
    EventBus.$on('resetView', () => {
      this.levelSelected = 'subsystem';
      EventBus.$emit('showSVGmap', 'wholemap', null, [], false);
    });
    EventBus.$on('GBnavigateTo', (type, id) => {
      // console.log(`on GB navigateTo ${type} ${id}`);
      this.goToTab(type, id);
    });
    window.addEventListener('click', () => {
      EventBus.$emit('hideSearchResult');
    });
  },
  methods: {
    setup() {
      if (this.$route.name === 'browser' || this.$route.name === 'browserRoot') {
        this.selectedType = this.$route.params.type || '';
        this.model = this.$route.params.model || '';
        this.componentID = this.$route.params.id || '';
        if (!this.componentID || !this.selectedType) {
          this.$router.push(`/Explore/browser/${this.model}`);
        }
      }
    },
    goToTab(type, componentID) {
      this.$router.push(`/Explore/browser/${this.model}/${type}/${componentID}`);
    },
    showGemsViewer() {
      EventBus.$emit('showGemsViewer');
    },
    showWholeMap() {
      EventBus.$emit('showSVGmap', 'wholemap', null, [], false);
    },
    imgUrl(path) {
      return this.dBImageSources(path);
    },
  },
};

</script>

<style lang="scss">
</style>
