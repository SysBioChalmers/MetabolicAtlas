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
          <h4 class="title is-4">Explore {{ model }} with the {{ messages.gemBrowserName }}</h4>
        </div>
      </div>
      <div class="columns is-centered">
        <global-search :quickSearch=true :model="model" ref="globalSearch"></global-search>
      </div>
      <div v-if="selectedType === ''">
        <div class="columns is-centered">
          <div class="column is-10 is-size-5 has-text-centered">
            Use the search field above to look for your constituent of interest.<br>
            Below is a list of popular constituents of {{ model }}.<br><br>
          </div>
        </div>
        <div class="tile is-ancestor is-size-5">
          <div class="tile">
            <div class="tile is-vertical is-9">
              <div class="tile">
                <tile type="reaction" :model="model" :data="starredComponents[model].reaction[0]">
                </tile>
                <div class="tile is-vertical is-8">
                  <tile type="subsystem" :model="model" :data="starredComponents[model].subsystem[0]">
                  </tile>
                  <div class="tile">
                    <tile type="enzyme" size="is-6" :model="model" :data="starredComponents[model].enzyme[0]">
                    </tile>
                    <tile type="metabolite" size="is-6" :model="model" :data="starredComponents[model].metabolite[0]">
                    </tile>
                  </div>
                </div>
              </div>
              <div class="tile">
                <div class="tile is-vertical is-8">
                  <div class="tile">
                    <tile type="subsystem" :model="model" :data="starredComponents[model].subsystem[1]">
                    </tile>
                  </div>
                  <div class="tile">
                    <tile type="metabolite" size="is-6" :model="model" :data="starredComponents[model].metabolite[1]">
                    </tile>
                    <tile type="enzyme" size="is-6" :model="model" :data="starredComponents[model].enzyme[1]">
                    </tile>
                  </div>
                </div>
                <div class="tile is-4">
                  <tile type="reaction" :model="model" :data="starredComponents[model].reaction[1]">
                  </tile>
                </div>
              </div>
            </div>
            <div class="tile is-vertical">
              <tile type="compartment" :model="model" :data="starredComponents[model].compartment[0]">
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
import GlobalSearch from 'components/explorer/GlobalSearch';
import ClosestInteractionPartners from 'components/explorer/gemBrowser/ClosestInteractionPartners';
import Enzyme from 'components/explorer/gemBrowser/Enzyme';
import Metabolite from 'components/explorer/gemBrowser/Metabolite';
import Reaction from 'components/explorer/gemBrowser/Reaction';
import Subsystem from 'components/explorer/gemBrowser/Subsystem';
import Compartment from 'components/explorer/gemBrowser/Compartment';
import { default as EventBus } from '../../event-bus';
import { idfy } from '../../helpers/utils';
import { default as messages } from '../../helpers/messages';
import Tile from './Tile';

export default {
  name: 'gem-browser',
  components: {
    ClosestInteractionPartners,
    Enzyme,
    Metabolite,
    Reaction,
    Subsystem,
    Compartment,
    GlobalSearch,
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
      model: '',
      starredComponents: {
        hmr2: {
          metabolite: [
            { name: '3-carboxy-1-hydroxypropyl-ThPP',
              id: 'm00765m',
              formula: 'magic formula',
              reaction_count: 45,
              compartment: 'cytosol' },
            { name: 'acetaldehyde',
              id: 'm01249m',
              formula: 'magic formula',
              reaction_count: 54,
              compartment: 'cytosol' },
          ],
          enzyme: [
            { name: 'ACLY',
              id: 'ENSG00000131473',
              reactions: 3,
              sub_count: 2,
              comp_count: 3 },
            { name: 'ACO1',
              id: 'ENSG00000122729',
              reactions: 3,
              sub_count: 2,
              comp_count: 3 },
          ],
          reaction: [
            { name: 'HMR_0710',
              id: 'HMR_0710',
              equation: 'isocitrate + NADP+ ⇒ AKG + CO2 + NADPH',
              sub_count: 2,
              comp_count: 1,
              e_count: 0 },
            { name: 'HMR_3787',
              id: 'HMR_3787',
              equation: 'isocitrate + NADP+ ⇒ AKG + CO2 + NADPH',
              sub_count: 3,
              comp_count: 2,
              e_count: 0 },
          ],
          subsystem: [
            { name: 'Valine, leucine, and isoleucine metabolism',
              id: '',
              reactions: 42,
              metabolites: 42,
              enzymes: 42,
              comp_count: 3 },
            { name: 'Phosphatidylinositol phosphate metabolism ',
              id: '',
              reactions: 42,
              metabolites: 42,
              enzymes: 42,
              comp_count: 3 },
          ],
          compartment: [
            { name: 'Peroxisome',
              id: 'peroxisome',
              reactions: 42,
              subsystems: [
                'Valine, leucine, and isoleucine metabolism',
                'Phosphatidylinositol phosphate metabolism ',
                'Phosphatidylinositol phosphate metabolism ',
                'Phosphatidylinositol phosphate metabolism ',
                'Phosphatidylinositol phosphate metabolism ',
                'Phosphatidylinositol phosphate metabolism ',
              ],
            },
          ],
        },
        yeast: {
          metabolite: [],
          enzyme: [],
          reaction: [],
        },
      },
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

    EventBus.$on('resetView', () => {
      this.levelSelected = 'subsystem';
      EventBus.$emit('showSVGmap', 'wholemap', null, [], false);
    });
    EventBus.$on('GBnavigateTo', (type, id) => {
      this.$router.push(`/explore/gem-browser/${this.model}/${type}/${idfy(id)}`);
    });
  },
  methods: {
    setup() {
      if (this.$route.name === 'browser' || this.$route.name === 'browserRoot') {
        this.model = this.$route.params.model || '';
        if (!(this.model in this.starredComponents)) {
          // TODO use another way to check the model id is valid
          this.model = '';
          EventBus.$emit('modelSelected', '');
          this.errorMessage = `Error: ${messages.modelNotFound}`;
          return;
        }
        this.selectedType = this.$route.params.type || '';
        this.componentID = this.$route.params.id || '';
        if (!this.componentID || !this.selectedType) {
          this.$router.push(`/explore/gem-browser/${this.model}`);
        }
      }
    },
    showMapViewer() {
      EventBus.$emit('showMapViewer');
    },
    showWholeMap() {
      EventBus.$emit('showSVGmap', 'wholemap', null, [], false);
    },
  },
};

</script>

<style lang="scss">

.homeDiv {
  margin-top: 3rem;
}

</style>
