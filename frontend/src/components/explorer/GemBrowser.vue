<template>
  <div class="section extended-section">
    <div class="container is-fullhd">
      <template v-if="errorMessage">
        <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
          {{ errorMessage }}
        </div>
      </template>
      <template v-else>
        <div class="columns">
          <div class="column container is-fullhd has-text-centered">
            <h3 class="title is-3">
              Explore {{ model ? model.short_name : 'a model' }} with the {{ messages.gemBrowserName }}
            </h3>
            <h5 class="subtitle is-5 has-text-weight-normal">
              use the menu bar search to find the component of interest
            </h5>
          </div>
        </div>
        <div>
          <div class="columns is-centered">
            <div class="column is-10 has-text-centered">
              <a id="randomButton" class="button is-rounded is-outlined is-success"
                 :class="tileComponents ? '' : 'is-loading'"
                 title="Fetch another random set of components" @click="getTilesData()">
                <span class="icon">
                  <i class="fa fa-random"></i>
                </span>
                <span v-if="model">random components of {{ model.short_name || 'a model' }}</span>
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
      </template>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import Tile from '@/components/explorer/gemBrowser/Tile';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'GemBrowser',
  components: {
    Tile,
  },
  data() {
    return {
      messages,
      errorMessage: '',
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      tileComponents: state => state.browserTiles.tileComponents,
    }),
  },
  async beforeMount() {
    if (!this.model || this.model.short_name !== this.$route.params.model) {
      const modelSelectionSuccessful = await this.$store.dispatch('models/selectModel', this.$route.params.model);
      if (!modelSelectionSuccessful) {
        this.errorMessage = `Error: ${messages.modelNotFound}`;
        return;
      }
    }
    await this.getTilesData();
  },
  methods: {
    async getTilesData() {
      await this.$store.dispatch('browserTiles/getBrowserTiles', this.model);
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
