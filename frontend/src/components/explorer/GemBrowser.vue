<template>
  <div>
    <template v-if="errorMessage">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </template>
    <template v-else>
      <div v-if="!selectedType" class="columns">
        <div class="column container is-fullhd has-text-centered">
          <h3 class="title is-3">Explore {{ model.short_name }} with the {{ messages.gemBrowserName }}</h3>
          <h5 class="subtitle is-5 has-text-weight-normal">
            use the search field to find the component of interest
          </h5>
        </div>
      </div>
      <div class="columns is-centered">
        <gem-search ref="gemSearch" />
      </div>
      <div v-if="showTiles && !selectedType">
        <div class="columns is-centered">
          <div class="column is-10 has-text-centered">
            <br><br>
            <a id="randomButton" class="button is-rounded is-outlined is-success"
               title="Fetch another random set of components" @click="getTilesData()">
              <span class="icon">
                <i class="fa fa-random"></i>
              </span>
              <span>random components of {{ model.short_name }}</span>
            </a>
            <br>
          </div>
        </div>
        <div v-if="tileComponents" id="gem-browser-tiles" class="tile is-ancestor">
          <div class="tile">
            <div class="tile is-vertical is-9">
              <div class="tile">
                <tile type="reaction" :data="tileComponents.reactions[0]">
                </tile>
                <div class="tile is-vertical is-8">
                  <tile type="subsystem" :data="tileComponents.subsystems[0]">
                  </tile>
                  <div class="tile">
                    <tile type="gene" size="is-6"
                          :data="tileComponents.genes[0]">
                    </tile>
                    <tile type="metabolite" size="is-6"
                          :data="tileComponents.metabolites[0]">
                    </tile>
                  </div>
                </div>
              </div>
              <div class="tile">
                <div class="tile is-vertical is-8">
                  <div class="tile">
                    <tile type="subsystem" :data="tileComponents.subsystems[1]">
                    </tile>
                  </div>
                  <div class="tile">
                    <tile type="metabolite" size="is-6"
                          :data="tileComponents.metabolites[1]">
                    </tile>
                    <tile type="gene" size="is-6"
                          :data="tileComponents.genes[1]">
                    </tile>
                  </div>
                </div>
                <div class="tile is-4">
                  <tile type="reaction" :data="tileComponents.reactions[1]">
                  </tile>
                </div>
              </div>
            </div>
            <div class="tile is-vertical">
              <tile type="compartment" :data="tileComponents.compartment">
              </tile>
            </div>
          </div>
        </div>
      </div>
      <div v-show="selectedType">
        <gene v-if="selectedType==='gene'" />
        <metabolite v-if="selectedType==='metabolite'" />
        <reaction v-if="selectedType==='reaction'" />
        <subsystem v-if="selectedType==='subsystem'" />
        <compartment v-if="selectedType==='compartment'" />
      </div>
    </template>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import GemSearch from '@/components/explorer/gemBrowser/GemSearch';
import Gene from '@/components/explorer/gemBrowser/Gene';
import Metabolite from '@/components/explorer/gemBrowser/Metabolite';
import Reaction from '@/components/explorer/gemBrowser/Reaction';
import Subsystem from '@/components/explorer/gemBrowser/Subsystem';
import Compartment from '@/components/explorer/gemBrowser/Compartment';
import Tile from '@/components/explorer/gemBrowser/Tile';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'GemBrowser',
  components: {
    Gene,
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

      showTiles: true,
      errorMessage: '',
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      tileComponents: state => state.browserTiles.tileComponents,
    }),
  },
  // TODO: remove selectedType and nested components, use router for navigation
  watch: {
    /* eslint-disable quote-props */
    '$route': async function watchSetup(newRoute, lastRoute) {
      this.selectedType = '';
      const loadTiles = !this.tileComponents || !(newRoute.name === 'browserRoot' && lastRoute.name === 'browser');
      await this.setup(loadTiles);
    },
  },
  async beforeMount() {
    await this.setup();
  },
  methods: {
    async setup(loadTiles = true) {
      if (['browser', 'browserRoot'].includes(this.$route.name)) {
        if (!this.model || this.model.database_name !== this.$route.params.model) {
          this.errorMessage = `Error: ${messages.modelNotFound}`;
          return;
        }
        if (this.$route.name === 'browserRoot' && loadTiles) {
          await this.getTilesData();
        } else if (this.selectedType === 'interaction') {
          this.$router.replace(`/explore/interaction/${this.model.database_name}/${this.componentID}`);
        } else {
          this.$store.dispatch('reactions/clearRelatedReactions');
          this.selectedType = this.$route.params.type;
        }
        this.showTiles = this.tileComponents !== null;
      }
    },
    async getTilesData() {
      try {
        await this.$store.dispatch('browserTiles/getBrowserTiles', this.model);
        this.showTiles = true;
      } catch {
        this.errorMessage = messages.unknownError;
        this.showTiles = false;
      }
    },
  },
};

</script>

<style lang="scss">

#gem-browser-tiles {
  word-wrap: anywhere;
  .tile.is-child {
    ul {
      list-style-type: disc;
      margin-left: 2rem;
    }
  }
}

#randomButton {
  vertical-align: inherit;
}

</style>
