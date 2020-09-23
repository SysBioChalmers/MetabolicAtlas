<template>
  <div id="mapViewer" class="extended-section">
    <div id="mapViewerContainer" class="columns">
      <template v-if="errorMessage">
        <div class="column is-danger is-half is-offset-one-quarter">
          <div class="notification is-danger is-danger has-text-centered">{{ errorMessage }}</div>
        </div>
      </template>
      <template v-else>
        <div id="mapSidebar"
             class="column is-one-fifth-widescreen is-one-quarter-desktop
                    is-one-quarter-tablet is-half-mobile has-background-lightgray">
          <Menu :maps-listing="mapsListing" />
        </div>
        <div v-if="currentMap" id="graphframe" class="column is-unselectable">
          <Svgmap v-if="showing2D"
                  :map-data="currentMap"
                  @loadComplete="handleLoadComplete"
                  @unSelect="unSelect" @updatePanelSelectionData="updatePanelSelectionData">
          </Svgmap>
          <ThreeDViewer v-if="!showing2D"
                        :component-id="requestedName"
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
             class="column is-narrow has-text-white is-unselectable" :class="{
               'is-paddingless': dataOverlayPanelVisible }"
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
        <DataOverlay v-if="currentMap !== null && dataOverlayPanelVisible" :map-name="currentMap.name" />
      </template>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
// import { debounce } from 'vue-debounce';
import Menu from '@/components/explorer/mapViewer/Menu.vue';
import DataOverlay from '@/components/explorer/mapViewer/DataOverlay.vue';
import Svgmap from '@/components/explorer/mapViewer/Svgmap';
import ThreeDViewer from '@/components/explorer/ThreeDviewer';
import { default as messages } from '@/helpers/messages';
import { default as EventBus } from '@/event-bus';

export default {
  name: 'MapViewer',
  components: {
    Menu,
    DataOverlay,
    Svgmap,
    ThreeDViewer,
  },
  data() {
    return {
      // already refactored
      dataOverlayPanelVisible: true,
      currentMap: null,

      // old
      errorMessage: '',
      loadMapErrorMessage: '',
      showOverviewScreen: true,
      requestedName: '',
      watchURL: true,

      selectionData: {
        type: '',
        data: null,
        error: false,
      },
      lastRoute: {},
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      showing2D: state => state.maps.showing2D,
    }),
    ...mapGetters({
      mapsListing: 'maps/mapsListing',
      queryParams: 'maps/queryParams',
    }),
  },
  watch: {
    '$route.params': 'loadMapFromParams',
  },
  // created() {
  //   this.handleQueryParamsWatch = debounce(this.handleQueryParamsWatch, 100);
  //   window.onpopstate = this.handleQueryParamsWatch();
  //   EventBus.$off('loadRNAComplete');
  //   EventBus.$on('loadRNAComplete', (isSuccess, errorMessage) => {
  //     if (!isSuccess) {
  //       this.showMessage(errorMessage);
  //       EventBus.$emit('unselectFirstTissue');
  //       EventBus.$emit('unselectSecondTissue');
  //     }
  //   });
  // },
  async created() {
    if (!this.model || this.model.short_name !== this.$route.params.model) {
      const modelSelectionSuccessful = await this.$store.dispatch('models/selectModel', this.$route.params.model);
      if (!modelSelectionSuccessful) {
        console.log(`Error: ${messages.modelNotFound}`);
      }
    }
    await this.$store.dispatch('maps/getMapsListing', this.model);
    this.$store.dispatch('maps/initFromQueryParams', this.$route.query);
    this.loadMapFromParams();
  },
  methods: {
    loadMapFromParams() {
      const id = this.$route.params.map_id;
      if (id) {
        /* eslint-disable prefer-destructuring */
        this.currentMap = this.mapsListing.compartments
          .concat(this.mapsListing.subsystems).filter(map => map.id === id)[0];
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
#mapViewer {
  #mapViewerContainer {
    margin-bottom: 0;
    min-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    max-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    height: calc(100vh - #{$navbar-height} - #{$footer-height});
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
  }

  .overlay {
    position: absolute;
    z-index: 10;
    padding: 10px;
    border-radius: 5px;
    background: rgba(22, 22, 22, 0.8);
  }

  .canvasOption {
    top: 7.25rem;
    left: 2.25rem;
    span {
      display: block;
      &:not(:last-child) {
        margin-bottom: 5px;
      }
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
  }

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
