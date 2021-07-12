<template>
  <div class="extended-section">
    <div id="mapViewerContainer" class="columns ordered-mobile m-0">
      <template v-if="errorMessage">
        <div class="column is-danger is-half is-offset-one-quarter">
          <div class="notification is-danger is-danger has-text-centered">{{ errorMessage }}</div>
        </div>
      </template>
      <template v-else>
        <MissingReactionModal :current-map="currentMap"
                              :missing-reaction-list="missingReactionList"
                              :map-reaction-list="mapReactionList"
                              :show-modal.sync="showModal" />
        <div id="mapSidebar" ref="mapSidebar"
             class="column is-one-fifth-widescreen is-one-quarter-desktop
                    is-one-quarter-tablet has-background-lightgray om-2 pt-0
                    fixed-height-desktop scrollable"
             v-on="sidebarLayoutReset ? { scroll: () => handleSidebarScroll() } : {}">
          <div id="mapSidebar__header" class="has-background-lightgray pt-3">
            <div class="buttons has-addons is-centered padding-mobile m-0"
                 :title="`Switch to ${dimensionalState(!showing2D) }`"
                 @click="currentMap && currentMap.type !== 'custom' && $store.dispatch('maps/toggleShowing2D')">
              <button v-for="dim in [true, false]" :key="dim"
                      class="button m-0"
                      :class="dim === showing2D ? 'is-selected is-primary has-text-weight-bold' : 'is-light'"
                      :disabled="currentMap && currentMap.type === 'custom'">
                <span v-if="dim === showing2D" class="icon">
                  <i class="fa fa-check-square-o"></i>
                </span>
                <span v-if="dim !== showing2D">Switch to&nbsp;</span>
                <span class="is-uppercase">{{ dimensionalState(dim) }}</span>
              </button>
            </div>
            <SidebarDataPanels ref="sidebarDataPanels"
                               :dim="dimensionalState(showing2D)"
                               :current-map="currentMap"
                               :selection-data="selectionData"
                               :show-modal.sync="showModal"
                               :missing-reaction-list="missingReactionList"
                               @openSelectionCardContent="resetSidebarLayout" />
          </div>
          <div class="padding-mobile">
            <a class="button is-fullwidth is-primary is-inverted has-text-weight-bold is-hidden-tablet"
               @click="showingMapListing = !showingMapListing">
              {{ showingMapListing ? 'Hide' : 'Show' }} the map list
            </a>
          </div>
          <a class="button is-fullwidth is-primary is-inverted has-text-weight-bold is-hidden-tablet"
             @click="$store.dispatch('maps/toggleDataOverlayPanelVisible')">
            {{ dataOverlayPanelVisible ? 'Hide' : 'Show' }} data overlay
          </a>
          <MapsListing v-if="showingMapListing" />
        </div>
        <div v-if="!currentMap"
             class="column is-unselectable om-1 fixed-height-mobile p-0 m-0">
          <NotFound v-if="mapNotFound" type="map" :component-id="$route.params.map_id"></NotFound>
          <p v-else class="is-size-5 has-text-centered" style="padding: 10%;">
            <a @click="showingMapListing = true">Show the map list and choose a compartment or subsystem map</a>
          </p>
        </div>
        <div v-else class="column is-unselectable om-1 fixed-height-desktop fixed-height-mobile p-0 m-0">
          <Svgmap v-if="showing2D"
                  :map-data="currentMap"
                  @unSelect="unSelect" @updatePanelSelectionData="updatePanelSelectionData">
          </Svgmap>
          <ThreeDViewer v-if="!showing2D"
                        :current-map="currentMap"
                        @unSelect="unSelect"
                        @updatePanelSelectionData="updatePanelSelectionData" />
          <ErrorPanel :message="loadMapErrorMessage" @hideErrorPanel="loadMapErrorMessage=''" />
        </div>
        <div id="dataOverlayBar"
             class="column is-narrow has-text-white is-unselectable is-hidden-mobile fixed-height-desktop p-1"
             :class="{'px-0 py-0': dataOverlayPanelVisible }"
             title="Click to show the data overlay panel"
             @click="$store.dispatch('maps/toggleDataOverlayPanelVisible')">
          <p class="is-size-5 has-text-centered has-text-weight-bold">
            <span class="icon py-2">
              <i class="fa"
                 :class="{ 'fa-arrow-left': !dataOverlayPanelVisible, 'fa-arrow-right': dataOverlayPanelVisible}">
              </i>
            </span><br>
            D<br>A<br>T<br>A<br><br>
            O<br>V<br>E<br>R<br>L<br>A<br>Y<br>
            <span class="icon">
              <i class="fa"
                 :class="{ 'fa-arrow-left': !dataOverlayPanelVisible, 'fa-arrow-right': dataOverlayPanelVisible}">
              </i>
            </span>
          </p>
        </div>
        <DataOverlay v-if="currentMap !== null && dataOverlayPanelVisible"
                     class="om-3 fixed-height-desktop scrollable" :map-name="currentMap.name" />
      </template>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import { debounce } from 'vue-debounce';
import DataOverlay from '@/components/explorer/mapViewer/DataOverlay.vue';
import ErrorPanel from '@/components/shared/ErrorPanel';
import MapsListing from '@/components/explorer/mapViewer/MapsListing.vue';
import MissingReactionModal from '@/components/explorer/mapViewer/MissingReactionModal.vue';
import NotFound from '@/components/NotFound';
import SidebarDataPanels from '@/components/explorer/mapViewer/SidebarDataPanels.vue';
import Svgmap from '@/components/explorer/mapViewer/Svgmap';
import ThreeDViewer from '@/components/explorer/mapViewer/ThreeDviewer';
import { default as messages } from '@/helpers/messages';
import { default as EventBus } from '@/event-bus';

export default {
  name: 'MapViewer',
  components: {
    DataOverlay,
    ErrorPanel,
    MapsListing,
    NotFound,
    SidebarDataPanels,
    Svgmap,
    ThreeDViewer,
    MissingReactionModal,
  },
  data() {
    return {
      showingMapListing: true,
      currentMap: null,
      errorMessage: '',
      loadMapErrorMessage: '',
      selectionData: {
        type: '',
        data: null,
        error: false,
      },
      mapNotFound: false,
      messages,
      sidebarLayoutReset: true,
      showModal: false,
      mapReactionList: null,
      missingReactionList: null,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      showing2D: state => state.maps.showing2D,
      dataOverlayPanelVisible: state => state.maps.dataOverlayPanelVisible,
      mapsListing: state => state.maps.mapsListing,
    }),
    ...mapGetters({
      queryParams: 'maps/queryParams',
    }),
  },
  watch: {
    '$route.params': 'loadMapFromParams',
    queryParams(newQuery, oldQuery) {
      this.handleQueryParamsWatch(newQuery, oldQuery);
    },
  },
  async created() {
    this.handleQueryParamsWatch = debounce(this.handleQueryParamsWatch, 100);
    window.onpopstate = this.handleQueryParamsWatch();

    EventBus.$off('loadRNAComplete');
    EventBus.$on('loadRNAComplete', (isSuccess, errorMessage) => {
      if (!isSuccess) {
        this.showMessage(errorMessage);
        EventBus.$emit('unselectFirstTissue');
        EventBus.$emit('unselectSecondTissue');
      }
    });
    if (!this.model || this.model.short_name !== this.$route.params.model) {
      const modelSelectionSuccessful = await this.$store.dispatch('models/selectModel', this.$route.params.model);
      if (!modelSelectionSuccessful) {
        this.errorMessage = `Error: ${messages.modelNotFound}`;
      }
    }
    await this.$store.dispatch('maps/getMapsListing', this.model);
    this.$store.dispatch('maps/initFromQueryParams', this.$route.query);
    this.loadMapFromParams();
  },
  methods: {
    handleSidebarScroll() {
      if (this.$refs.mapSidebar.scrollTop > 0) {
        this.sidebarLayoutReset = false;
        this.$refs.sidebarDataPanels.hideSelectionCardContent();
      }
    },
    resetSidebarLayout() {
      this.$refs.mapSidebar.scrollTop = 0;
      this.sidebarLayoutReset = true;
    },
    dimensionalState(showing2D) {
      return showing2D ? '2d' : '3d';
    },
    handleQueryParamsWatch(newQuery, oldQuery) {
      if (newQuery && !this.$route.params.map_id) {
        const payload = [{}, null, `${this.$route.path}?dim=${newQuery.dim}`];
        history.replaceState(...payload); // eslint-disable-line no-restricted-globals
        return;
      }

      if (JSON.stringify(newQuery) === JSON.stringify(oldQuery)) {
        return;
      }

      const queryString = Object.entries(newQuery).map(e => e.join('=')).join('&');

      const payload = [{}, null, `${this.$route.path}?${queryString}`];
      if (newQuery.dim === this.$route.query.dim || (newQuery.dim && !this.$route.query.dim)) {
        history.replaceState(...payload); // eslint-disable-line no-restricted-globals
      } else {
        history.pushState(...payload); // eslint-disable-line no-restricted-globals
      }
    },
    loadMapFromParams() {
      const id = this.$route.params.map_id;
      if (id) {
        const categories = Object.keys(this.mapsListing);
        const items = Object.values(this.mapsListing);
        for (let i = 0; i < categories.length; i += 1) {
          for (let j = 0; j < items[i].length; j += 1) {
            const item = items[i][j];
            if (this.showing2D) {
              for (let k = 0; k < item.svgs.length; k += 1) {
                if (item.svgs[k].id === id) {
                  this.currentMap = { ...item };
                  this.currentMap.svgs = [item.svgs[k]];
                  this.currentMap.mapReactionIdSet = item.svgs;
                  this.currentMap.type = categories[i].slice(0, -1);
                  this.mapNotFound = false;
                  this.setMapReactionList();
                  this.setMissingReactionList();
                  return;
                }
              }
            } else if (item.id === id) {
              this.currentMap = item;
              this.currentMap.type = categories[i].slice(0, -1);
              this.mapNotFound = false;
              this.currentMap.mapReactionIdSet = item.svgs;
              this.setMapReactionList();
              this.setMissingReactionList();
              return;
            }
            this.mapNotFound = true;
          }
        }
      }
    },
    setMapReactionList() {
      let mapReactionIdList = [];
      this.currentMap.mapReactionIdSet.forEach((map) => {
        mapReactionIdList = [...mapReactionIdList, ...map.mapReactionIdSet];
      });
      this.mapReactionList = mapReactionIdList;
    },
    setMissingReactionList() {
      const modelReactionIdSet = new Set(this.currentMap.reactionList);
      const mapReactionIdSet = new Set(this.mapReactionList);
      const missingReactionIdSet = new Set([...modelReactionIdSet].filter(x => !mapReactionIdSet.has(x)));
      this.missingReactionList = Array.from(missingReactionIdSet);
    },
    showMessage(errorMessage) {
      this.loadMapErrorMessage = errorMessage;
      if (!this.loadMapErrorMessage) {
        this.loadMapErrorMessage = messages.unknownError;
      }
    },
    unSelect() {
      this.selectionData.error = false;
      this.selectionData.data = null;
    },
    updatePanelSelectionData(data) {
      this.selectionData = data;
    },
  },
};
</script>

<style lang="scss">
#mapViewerContainer {

  #mapSidebar {
    word-wrap: break-word;

    &__header {
      @media screen and (min-width: $tablet) {
        position: sticky;
        top: 0;
        z-index: 1;
      }
    }

    .buttons {

      button {
        min-width: 8rem;
        width: 50%;

        &:focus {
          // This is needed because the box-shadow shows for certain browsers, for more info see:
          // https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#Clicking_and_focus
          box-shadow: none;
        }
      }
    }
  }

  .padding-mobile {
    @media screen and (max-width: $tablet) {
      padding-bottom: 0.75rem;
    }
  }

  .overlay {
    position: absolute;
    z-index: 10;
    border-radius: 5px;
    background: rgba(22, 22, 22, 0.8);
  }

  .canvasOption {
    top: 2rem;
    left: 1.5rem;
    span {
      display: block;
      &:not(:last-child) {
        margin-bottom: 5px;
      }
    }
  }

  @media screen and (max-width: $tablet) {
    &.ordered-mobile {
      display: flex;
      flex-flow: column;
    }
    .om-1 {
      order: 1;
    }
    .om-2 {
      order: 2;
    }
    .om-3 {
      order: 3;
    }
    .om-4 {
      order: 4;
    }
  }
}

.fixed-height-desktop {
  @media screen and (min-width: $tablet) {
    height: calc(100vh - #{$navbar-height} - #{$footer-height});
    overflow: hidden;

    &.scrollable {
      overflow-y: scroll;
    }
  }
}

.fixed-height-mobile {
  @media screen and (max-width: $tablet) {
    height: 450px;
  }
  position: relative;
}

#dataOverlayBar {
  display: flex;
  align-items: center;
  background: $primary;
  cursor: pointer;
  line-height: 17px;
  &:hover{
    background: $primary-light;
  }
  @media (max-width: $tablet) {
    display: none;
  }
}
</style>
