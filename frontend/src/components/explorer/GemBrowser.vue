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
      <div class="columns is-centered" v-if="selectedType === ''">
        <div class="column is-10 is-size-5 has-text-centered">
          Use the search field above to look for your constituent of interest.
          Below is a list of popular constituents of {{ model }}.
        </div>
      </div>
      <div class="homeDiv columns has-text-centered" v-if="selectedType === '' && starredComponents[model]">
        <div class="column is-4" v-for="category in ['metabolite', 'enzyme', 'reaction']">
          <h5 class="title is-size-5 is-capitalized">{{ category }}s</h5>
          <router-link v-for="row in starredComponents[model][category]" :to="{ path: `/explore/gem-browser/${model}/${category}/${row[1]}` }"
            v-if="model in starredComponents" class="is-block">
            {{ row[0] }}
          </router-link>
        </div>
      </div>
      <div v-else>
        <closest-interaction-partners v-if="selectedType==='interaction'" :model="model"></closest-interaction-partners>
        <enzyme v-if="selectedType==='enzyme'" :model="model"></enzyme>
        <metabolite v-if="selectedType==='metabolite'" :model="model"></metabolite>
        <reaction v-if="selectedType==='reaction'" :model="model"></reaction>
        <subsystem v-if="selectedType==='subsystem'" :model="model"></subsystem>
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
import { default as EventBus } from '../../event-bus';
import { idfy } from '../../helpers/utils';
import { default as messages } from '../../helpers/messages';


export default {
  name: 'gem-browser',
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
            ['3-carboxy-1-hydroxypropyl-ThPP', 'm00765m'],
            ['acetaldehyde', 'm01249m'],
            ['acetate', 'm01252m'],
            ['acetoacetate', 'm01253m'],
            ['acetoacetyl-CoA', 'm01255m'],
            ['acetyl-CoA', 'm01261m'],
            ['cis-aconitate', 'm01580m'],
            ['citrate', 'm01587m'],
            ['dihydrolipoamide', 'm01701m'],
            ['fumarate', 'm01862m'],
            ['glycolaldehyde', 'm01997m'],
            ['glycolate', 'm01998m'],
            ['glyoxalate', 'm02007m'],
            ['hydroxypyruvate', 'm02154m'],
            ['isocitrate', 'm02183m'],
            ['lipoamide', 'm02393m'],
            ['malate', 'm02439m'],
            ['oxalosuccinate', 'm02662m'],
            ['pyruvate', 'm02819m'],
            ['S-acetyldihydrolipoamide', 'm02869m'],
            ['S-succinyldihydrolipoamide', 'm02934m'],
            ['succinate', 'm02943m'],
            ['succinyl-CoA', 'm02944m'],
            ['thiamin-PP', 'm02984m'],
            ['ubiquinol', 'm03102m'],
            ['ubiquinone', 'm03103m'],
          ],
          enzyme: [
            ['ACLY', 'ENSG00000131473'],
            ['ACO1', 'ENSG00000122729'],
            ['ACSS3', 'ENSG00000111058'],
            ['ACYP1', 'ENSG00000119640'],
            ['ADH1A', 'ENSG00000187758'],
            ['BPGM', 'ENSG00000172331'],
            ['CLYBL', 'ENSG00000125246'],
            ['CRISP3', 'ENSG00000096006'],
            ['FBP1', 'ENSG00000165140'],
            ['GAPDH', 'ENSG00000111640'],
            ['GRHPR', 'ENSG00000137106'],
            ['HCN3', 'ENSG00000143630'],
            ['HKDC1', 'ENSG00000156510'],
            ['IDH1', 'ENSG00000138413'],
            ['IREB2', 'ENSG00000136381'],
            ['KANK1', 'ENSG00000107104'],
            ['MIA3', 'ENSG00000154305'],
            ['OGDH', 'ENSG00000105953'],
            ['OXCT1', 'ENSG00000083720'],
            ['PDHA1', 'ENSG00000131828'],
            ['PGK1', 'ENSG00000102144'],
            ['SUCLA2', 'ENSG00000136143'],
            ['TMEM54', 'ENSG00000121900'],
            ['TPI1P2', 'ENSG00000230359'],
            ['UEVLD', 'ENSG00000151116'],
            ['ZADH2', 'ENSG00000180011'],
          ],
          reaction: [
            ['HMR_0710', 'HMR_0710'],
            ['HMR_3787', 'HMR_3787'],
            ['HMR_3905', 'HMR_3905'],
            ['HMR_3957', 'HMR_3957'],
            ['HMR_4097', 'HMR_4097'],
            ['HMR_4108', 'HMR_4108'],
            ['HMR_4111', 'HMR_4111'],
            ['HMR_4133', 'HMR_4133'],
            ['HMR_4209', 'HMR_4209'],
            ['HMR_4281', 'HMR_4281'],
            ['HMR_4301', 'HMR_4301'],
            ['HMR_4388', 'HMR_4388'],
            ['HMR_4391', 'HMR_4391'],
            ['HMR_4408', 'HMR_4408'],
            ['HMR_4521', 'HMR_4521'],
            ['HMR_4585', 'HMR_4585'],
            ['HMR_4652', 'HMR_4652'],
            ['HMR_5294', 'HMR_5294'],
            ['HMR_6410', 'HMR_6410'],
            ['HMR_7704', 'HMR_7704'],
            ['HMR_7745', 'HMR_7745'],
            ['HMR_8360', 'HMR_8360'],
            ['HMR_8652', 'HMR_8652'],
            ['HMR_8757', 'HMR_8757'],
            ['HMR_8772', 'HMR_8772'],
            ['HMR_8780', 'HMR_8780'],
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
