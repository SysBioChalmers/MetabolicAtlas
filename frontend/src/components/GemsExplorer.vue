<template>
  <div class="network-graph">
    <div class="columns" v-if="!selectedTab">
      <div class="column container has-text-centered">
        <h4 class="title is-4">Browse through your favorite GEM</h4>
      </div>
    </div>
    <div class="columns">
      <div class="column is-2">
        <div class="button is-medium is-info" v-if="selectedTab" @click="showNetworkGraph()">
          {{ $t('metabolicViewer') }}
        </div>
      </div>
      <global-search
      :quickSearch=true
      :model="selectedModel"
      ></global-search>
    </div>
    <br>
    <div class="tabs is-boxed is-centered" v-if="selectedTab">
      <ul>
        <li
         v-for="tab in tabs"
         :class="[{ 'is-active': isActive(tab.type) }, { 'is-disabled': tab.type !== selectedTab }]"
         :disabled="tab.type !== selectedTab"
         @click="goToTab(tab.type, componentID)"
        >
         <a :class="{ 'disabled': tab.type !== selectedTab}"><span>{{ tab.title }}</span></a>
        </li>
      </ul>
    </div>
    <div v-if="errorMessage">
      {{ errorMessage }}
    </div>
    <div v-else>
      <closest-interaction-partners v-if="selectedTab==='interaction'" :model="selectedModel"></closest-interaction-partners>
      <enzyme v-if="selectedTab==='enzyme'" :model="selectedModel"></enzyme>
      <metabolite v-if="selectedTab==='metabolite'" :model="selectedModel"></metabolite>
      <reaction v-if="selectedTab==='reaction'" :model="selectedModel"></reaction>
      <subsystem v-if="selectedTab==='subsystem'" :model="selectedModel"></subsystem>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import GlobalSearch from 'components/GlobalSearch';
import ClosestInteractionPartners from 'components/ClosestInteractionPartners';
import Enzyme from 'components/Enzyme';
import Metabolite from 'components/Metabolite';
import Reaction from 'components/Reaction';
import Subsystem from 'components/Subsystem';
// import router from '../router';
import { default as EventBus } from '../event-bus';

export default {
  name: 'gems-explorer',
  components: {
    ClosestInteractionPartners,
    Enzyme,
    Metabolite,
    Reaction,
    Subsystem,
    GlobalSearch,
  },
  data() {
    return {
      selectedModel: 'hmr2',
      selectedTab: '',
      searchTerm: '',
      searchResults: [],
      errorMessage: '',
      componentID: '',
      tabs: [
        { title: this.$t('tab1title'), type: 'interaction' },
        { title: this.$t('tab2title'), type: 'enzyme' },
        { title: this.$t('tab3title'), type: 'metabolite' },
        { title: this.$t('tab4title'), type: 'reaction' },
        { title: this.$t('tab5title'), type: 'subsystem' },
      ],
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  created() {
    // init the global events
    EventBus.$on('resetView', () => {
      this.levelSelected = 'subsystem';
      EventBus.$emit('showSVGmap', 'wholemap', null, []);
    });
    EventBus.$on('updateSelTab', (type, id) => {
      console.log(`on updateSelTab ${type} ${id}`);
      this.goToTab(type, id);
    });
  },
  beforeMount() {
    this.setup();
  },
  methods: {
    setup() {
      console.log(this.$route);
      this.selectedTab = this.$route.params.type || '';
      this.selectedModels = this.$route.params.model || '';
      this.componentID = this.$route.params.id || '';
      if (!this.componentID || !this.selectedModels) {
        this.$router.push(`/GemsExplorer/${this.selectedModel}`);
      }
    },
    isActive(tabType) {
      return tabType === this.selectedTab;
    },
    goToTab(type, componentID) {
      if (!this.tabs.map(el => el.type).includes(type.toLowerCase())) {
        this.$router.push('/GemsExplorer');
        return;
      }
      this.$router.push(`/GemsExplorer/${this.selectedModel}/${type}/${componentID}`);
    },
    search() {
      if (this.searchTerm.length < 2) {
        return;
      }
      const searchTerm = this.searchTerm;
      this._.debounce(() => {
        axios.get(`search/${searchTerm}`)
          .then((response) => {
            this.searchResults = response.data;
          })
          .catch(() => {
            this.searchResults = [];
          });
      }, 500)();
    },
    selectSearchResult(tabIndex, componentID) {
      this.searchTerm = '';
      this.searchResults = [];
      this.goToTab(tabIndex, componentID);
    },
    showNetworkGraph() {
      EventBus.$emit('toggleNetworkGraph');
    },
  },
};

</script>

<style lang="scss">

a.disabled {
  cursor: default;
  color: lightgray;
}

.hero .tabs ul {
  border-bottom: 1px solid #dbdbdb;
}

</style>
