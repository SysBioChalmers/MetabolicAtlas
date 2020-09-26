<template>
  <div class="extended-section">
    <div id="mapViewerContainer" class="columns">
      <template v-if="errorMessage">
        <div class="column is-danger is-half is-offset-one-quarter">
          <div class="notification is-danger is-danger has-text-centered">{{ errorMessage }}</div>
        </div>
      </template>
      <template v-else>
        <div id="mapSidebar"
             class="column is-one-fifth-widescreen is-one-quarter-desktop
                    is-one-quarter-tablet has-background-lightgray om-2">
          <a class="button" @click="$store.dispatch('maps/toggleShowing2D')">
            Switch to {{ showing2D ? '3D' : '2D ' }}
          </a>
          <a class="button" @click="showingMapListing = !showingMapListing">
            {{ showingMapListing ? 'Hide' : 'Show' }} map list
          </a>
          <SidebarDataPanels
            :dim="showing2D ? '2d' : '3d'"
            :current-map="currentMap"
            :selection-data="selectionData"
            :loading="false" />
          <MapsListing v-if="showingMapListing" :maps-listing="mapsListing" />
        </div>
        <div v-if="currentMap" id="graphframe" class="column is-unselectable om-1">
          <Svgmap v-if="showing2D"
                  :map-data="currentMap"
                  @loadComplete="handleLoadComplete"
                  @unSelect="unSelect" @updatePanelSelectionData="updatePanelSelectionData">
          </Svgmap>
          <ThreeDViewer v-if="!showing2D"
                        :current-map="currentMap"
                        @loadComplete="handleLoadComplete"
                        @unSelect="unSelect"
                        @updatePanelSelectionData="updatePanelSelectionData" />
          <transition name="slide-fade">
            <article v-if="loadMapErrorMessage" id="errorPanel" class="message is-danger">
              <div class="message-header">
                <b>Oops!..</b>
              </div>
              <div class="message-body has-text-centered"><h5 class="title is-6">{{ loadMapErrorMessage }}</h5></div>
            </article>
          </transition>
        </div>
        <div v-else class="column">
          <p class="is-size-5 has-text-centered" style="padding: 10%;">
            Choose a compartment or subsystem map from the menu on the left
          </p>
        </div>
        <div id="dataOverlayBar"
             class="column is-narrow has-text-white is-unselectable is-hidden-mobile"
             :class="{'is-paddingless': dataOverlayPanelVisible }"
             title="Click to show the data overlay panel" @click="toggleDataOverlayPanel()">
          <p class="is-size-5 has-text-centered has-text-weight-bold">
            <span class="icon">
              <i class="fa"
                 :class="{ 'fa-arrow-left': !dataOverlayPanelVisible, 'fa-arrow-right': dataOverlayPanelVisible}"></i>
            </span><br>
            D<br>A<br>T<br>A<br><br>
            O<br>V<br>E<br>R<br>L<br>A<br>Y<br>
            <span class="icon">
              <i class="fa"
                 :class="{ 'fa-arrow-left': !dataOverlayPanelVisible, 'fa-arrow-right': dataOverlayPanelVisible}"></i>
            </span>
          </p>
        </div>
        <DataOverlay v-if="currentMap !== null && dataOverlayPanelVisible" class="om-3" :map-name="currentMap.name" />
      </template>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import { debounce } from 'vue-debounce';
import DataOverlay from '@/components/explorer/mapViewer/DataOverlay.vue';
import MapsListing from '@/components/explorer/mapViewer/MapsListing.vue';
import SidebarDataPanels from '@/components/explorer/mapViewer/SidebarDataPanels.vue';
import Svgmap from '@/components/explorer/mapViewer/Svgmap';
import ThreeDViewer from '@/components/explorer/mapViewer/ThreeDviewer';
import { default as messages } from '@/helpers/messages';
import { default as EventBus } from '@/event-bus';

export default {
  name: 'MapViewer',
  components: {
    DataOverlay,
    MapsListing,
    SidebarDataPanels,
    Svgmap,
    ThreeDViewer,
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
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      showing2D: state => state.maps.showing2D,
      dataOverlayPanelVisible: state => state.maps.dataOverlayPanelVisible,
    }),
    ...mapGetters({
      mapsListing: 'maps/mapsListing',
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
    handleQueryParamsWatch(newQuery, oldQuery) {
      if (!this.$route.params.map_id) {
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
                  this.currentMap.type = categories[i].slice(0, -1);
                  return;
                }
              }
            } else if (item.id === id) {
              this.currentMap = item;
              this.currentMap.type = categories[i].slice(0, -1);
              return;
            }
          }
        }
      }
    },
    handleLoadComplete(isSuccess, errorMessage) {
      if (!isSuccess) {
        this.selectionData.data = null;
        this.showMessage(errorMessage);
      }
      this.$nextTick(() => {
        EventBus.$emit('reloadGeneExpressionData');
      });
    },
    toggleDataOverlayPanel() {
      this.$store.dispatch('maps/toggleDataOverlayPanelVisible');
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
  height: calc(100vh - #{$navbar-height} - #{$footer-height});

  .overlay {
    position: absolute;
    z-index: 10;
    padding: 10px;
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

  @media (max-width: $tablet) {
    .ordered-mobile {
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

#graphframe {
  position: relative;
  height: 100%;
  padding: 0;
  margin: 0;
  overflow: hidden;
}

#dataOverlayBar {
  display: flex;
  align-items: center;
  background: $primary;
  cursor: pointer;
  line-height: 17px;
  padding: 0.25rem;
  .icon {
    padding-bottom: 20px;
    padding-top: 20px;
  }
  &:hover{
    background: $primary-light;
  }
  padding-right: 1rem;
  @media (max-width: $tablet) {
    display: none;
  }
}

#errorPanel {
  z-index: 11;
  position: absolute;
  left: 0;
  right: 0;
  margin-left: auto;
  margin-right: auto;
  width: 350px;
  bottom: 2rem;
  border: 1px solid gray;

  .slide-fade-enter-active {
    transition: all .3s ease;
  }
  .slide-fade-leave-active {
    transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0);
  }
  .slide-fade-enter, .slide-fade-leave-active {
    transform: translateY(200px);
    opacity: 0;
  }
}
</style>
