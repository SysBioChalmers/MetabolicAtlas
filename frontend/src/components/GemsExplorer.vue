<template>
  <section class="section extended-section">
    <div class="container">
      <div class="network-graph">
        <div class="columns" v-if="!selectedType">
          <div class="column container has-text-centered">
            <h4 class="title is-4">Browse through your favorite GEM</h4>
          </div>
        </div>
        <div class="columns">
          <div class="column is-3">
          </div>
          <global-search
          :quickSearch=true
          :model="selectedModel"
          ref="globalSearch"></global-search>
        </div>
        <div v-if="errorMessage">
          {{ errorMessage }}
        </div>
        <div v-else>
          <closest-interaction-partners v-if="selectedType==='interaction'" :model="selectedModel"></closest-interaction-partners>
          <enzyme v-if="selectedType==='enzyme'" :model="selectedModel"></enzyme>
          <metabolite v-if="selectedType==='metabolite'" :model="selectedModel"></metabolite>
          <reaction v-if="selectedType==='reaction'" :model="selectedModel"></reaction>
          <subsystem v-if="selectedType==='subsystem'" :model="selectedModel"></subsystem>
          <template v-if="selectedType===''">
            <div class="columns">
              <div class="column">
              </div>
            </div>
            <div class="columns">
              <div class="column has-text-centered">
                <span class="title is-4">Or visualize networks with the MetabolicViewer</span> 
                 <div class="has-text-centered">
                  <a @click="showMetabolicViewer">
                    <img width="500" :src="imgUrl('./metabolicViewer-600.jpg')" style="border: 1px solid black" />
                  </a>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import axios from 'axios';
import GlobalSearch from 'components/GlobalSearch';
import ClosestInteractionPartners from 'components/ClosestInteractionPartners';
import Enzyme from 'components/Enzyme';
import Metabolite from 'components/Metabolite';
import Reaction from 'components/Reaction';
import Subsystem from 'components/Subsystem';
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
  props: ['selectedModel'],
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
    this.dBImageSources = require.context('../assets', false, /\.(png|gif|jpg)$/);
    this.setup();
  },
  created() {
    if (this.$route.path.toLowerCase().includes('gemsexplorer')) {
      EventBus.$emit('showGemsExplorer');
    }
    // init the global events
    EventBus.$on('resetView', () => {
      this.levelSelected = 'subsystem';
      EventBus.$emit('showSVGmap', 'wholemap', null, [], false);
    });
    EventBus.$on('updateSelTab', (type, id) => {
      console.log(`on updateSelTab ${type} ${id}`);
      EventBus.$emit('showGemsExplorer');
      this.goToTab(type, id);
    });
    window.addEventListener('click', () => {
      EventBus.$emit('hideSearchResult');
    });
  },
  methods: {
    setup() {
      console.log(this.$route, '========');
      if (this.$route.name === 'GemsExplorerDefault') {
        this.$router.push({ path: '/' });
      }
      if (this.$route.path.toLowerCase().includes('gemsexplorer')) {
        this.selectedType = this.$route.params.type || '';
        this.selectedModel = this.$route.params.model || '';
        this.componentID = this.$route.params.id || '';
        if (!this.componentID || !this.selectedType) {
          this.$router.push(`/gemsExplorer/${this.selectedModel}`);
        }
      }
    },
    goToTab(type, componentID) {
      this.$router.push(`/gemsExplorer/${this.selectedModel}/${type}/${componentID}`);
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
    showMetabolicViewer() {
      EventBus.$emit('showMetabolicViewer');
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

.hero .tabs ul {
  border-bottom: 1px solid #dbdbdb;
}

.tabs li.is-disabled {
  pointer-events: none;
  opacity: .65;
}

</style>
