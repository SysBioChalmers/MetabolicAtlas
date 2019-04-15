<template>
  <div>
    <template v-if="errorMessage">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </template>
    <template v-else>
      <div class="columns" v-if="!selectedType">
        <div class="column container has-text-centered">
          <h4 class="title is-4">Explore {{ model.short_name }} with the {{ messages.gemBrowserName }}</h4>
        </div>
      </div>
      <div class="columns is-centered">
        <gem-search :model="model" ref="gemSearch"></gem-search>
      </div>
      <div v-if="selectedType === ''">
        <div class="columns is-centered">
          <div class="column is-10 is-size-5 has-text-centered">
            Use the search field above to look for your constituent of interest.<br>
            Below are some random constituents of {{ model.short_name }}.<br><br>
          </div>
        </div>
        <div id="gem-browser-tiles" class="tile is-ancestor is-size-5" v-if="starredComponents">
          <div class="tile">
            <div class="tile is-vertical is-9">
              <div class="tile">
                <tile type="reaction" :model="model" :data="starredComponents.reactions[0]">
                </tile>
                <div class="tile is-vertical is-8">
                  <tile type="subsystem" :model="model" :data="starredComponents.subsystems[0]">
                  </tile>
                  <div class="tile">
                    <tile type="enzyme" size="is-6" :model="model" :data="starredComponents.enzymes[0]">
                    </tile>
                    <tile type="metabolite" size="is-6" :model="model" :data="starredComponents.metabolites[0]">
                    </tile>
                  </div>
                </div>
              </div>
              <div class="tile">
                <div class="tile is-vertical is-8">
                  <div class="tile">
                    <tile type="subsystem" :model="model" :data="starredComponents.subsystems[1]">
                    </tile>
                  </div>
                  <div class="tile">
                    <tile type="metabolite" size="is-6" :model="model" :data="starredComponents.metabolites[1]">
                    </tile>
                    <tile type="enzyme" size="is-6" :model="model" :data="starredComponents.enzymes[1]">
                    </tile>
                  </div>
                </div>
                <div class="tile is-4">
                  <tile type="reaction" :model="model" :data="starredComponents.reactions[1]">
                  </tile>
                </div>
              </div>
            </div>
            <div class="tile is-vertical">
              <tile type="compartment" :model="model" :data="starredComponents.compartments[0]">
              </tile>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <closest-interaction-partners v-if="selectedType==='interaction'" :model="model"></closest-interaction-partners>
        <enzyme v-if="selectedType==='enzyme'" :model="model"></enzyme>
        <metabolite v-if="selectedType==='metabolite'" :model="model"></metabolite>
        <reaction v-if="selectedType==='reaction'" :model="model"></reaction>
        <subsystem v-if="selectedType==='subsystem'" :model="model"></subsystem>
        <compartment v-if="selectedType==='compartment'" :model="model"></compartment>
      </div>
    </template>
  </div>
</template>

<script>
import axios from 'axios';
import GemSearch from 'components/explorer/gemBrowser/GemSearch';
import ClosestInteractionPartners from 'components/explorer/gemBrowser/ClosestInteractionPartners';
import Enzyme from 'components/explorer/gemBrowser/Enzyme';
import Metabolite from 'components/explorer/gemBrowser/Metabolite';
import Reaction from 'components/explorer/gemBrowser/Reaction';
import Subsystem from 'components/explorer/gemBrowser/Subsystem';
import Compartment from 'components/explorer/gemBrowser/Compartment';
import Tile from 'components/explorer/gemBrowser/Tile';
import { default as messages } from '../../helpers/messages';
import { default as EventBus } from '../../event-bus';
import { idfy } from '../../helpers/utils';


export default {
  name: 'gem-browser',
  props: ['model'],
  components: {
    ClosestInteractionPartners,
    Enzyme,
    Metabolite,
    Reaction,
    Subsystem,
    Compartment,
    GemSearch,
    Tile,
  },
  data() {
    return {
      messages,
      selectedType: '',
      searchTerm: '',
      searchResults: [],
      errorMessage: '',
      componentID: '',
      mapsAvailable: null,
      starredComponents: null,
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  beforeMount() {
    this.setup();
  },
  created() {
    // init the global events
    EventBus.$off('resetView');
    EventBus.$off('GBnavigateTo');
    EventBus.$off('viewReactionOnMap');

    EventBus.$on('resetView', () => {
      this.levelSelected = 'subsystem';
      EventBus.$emit('showSVGmap', 'wholemap', null, [], false);
    });
    EventBus.$on('GBnavigateTo', (type, id) => {
      let ID = id;
      if (type === 'subsystem' || type === 'compartment') {
        ID = idfy(id);
      }
      this.$router.push(`/explore/gem-browser/${this.$route.params.model}/${type}/${ID}`);
    });
  },
  methods: {
    setup() {
      if (this.$route.name === 'browser' || this.$route.name === 'browserRoot') {
        if (!this.model || this.model.database_name !== this.$route.params.model) {
          EventBus.$emit('modelSelected', '');
          this.errorMessage = `Error: ${messages.modelNotFound}`;
          return;
        }
        this.selectedType = this.$route.params.type || '';
        this.componentID = this.$route.params.id || '';
        if (!this.componentID || !this.selectedType) {
          this.$router.push(`/explore/gem-browser/${this.model.database_name}`);
          if (!this.starredComponents) {
            this.get_tiles_data();
          }
        }
      }
    },
    get_tiles_data() {
      axios.get(`${this.model.database_name}/gem_browser_tiles/`)
      .then((response) => {
        this.starredComponents = response.data;
      })
      .catch(() => {
        this.errorMessage = messages.unknownError;
      });
    },
    showMapViewer() {
      EventBus.$emit('showMapViewer');
    },
  },
};

</script>

<style lang="scss">
</style>
