<template>
  <div id="mapViewer" class="extended-section">
    <div id="mapViewerContainer" class="columns">
      <template v-if="errorMessage">
        <div class="column is-danger is-half is-offset-one-quarter">
          <div class="notification is-danger is-danger has-text-centered">{{ errorMessage }}</div>
        </div>
      </template>
      <template v-else>
        <div class="column is-one-fifth-widescreen is-one-quarter-desktop
                    is-one-quarter-tablet is-half-mobile has-background-lightgray">
          <Menu />
        </div>
        <div v-show="showOverviewScreen" class="column">
          <p class="is-size-5 has-text-centered" style="padding: 10%;">
            Choose a compartment or subsystem map from the menu on the left
          </p>
        </div>
        <div v-show="!showOverviewScreen" id="graphframe" class="column is-unselectable">
          <Svgmap v-if="showing2D"
                  :maps-data="{ customName: 'Peroxisome', filename: 'peroxisome.svg', id: 'peroxisome'}"
                  requested-map-name="peroxisome"
                  @loadComplete="handleLoadComplete"
                  @loading="showLoader=true" @startSelection="showSelectionLoader=true" @endSelection="endSelection"
                  @unSelect="unSelect" @updatePanelSelectionData="updatePanelSelectionData">
          </Svgmap>
          <ThreeDViewer v-if="!showing2D"
                        :component-id="requestedName"
                        :loading="showLoader"
                        @loadComplete="handleLoadComplete"
                        @loading="showLoader=true" @startSelection="showSelectionLoader=true"
                        @endSelection="endSelection" @unSelect="unSelect"
                        @updatePanelSelectionData="updatePanelSelectionData" />
          <div v-show="showLoader" id="iLoader" class="loading">
            <a class="button is-loading"></a>
          </div>
          <transition name="slide-fade">
            <article v-if="loadMapErrorMessage" id="errorPanel" class="message is-danger">
              <div class="message-header">
                <b>Oops!..</b>
              </div>
              <div class="message-body has-text-centered"><h5 class="title is-6">{{ loadMapErrorMessage }}</h5></div>
            </article>
          </transition>
        </div>
        <div v-show="!showLoader" id="dataOverlayBar"
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
        <DataOverlay v-show="dataOverlayPanelVisible"
                     :dim="dim" :map-name="currentDisplayedName" />
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
import { default as EventBus } from '@/event-bus';
import { default as messages } from '@/helpers/messages';

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
      errorMessage: '',
      loadMapErrorMessage: '',
      showOverviewScreen: true,
      requestedName: '',
      currentDisplayedName: '',
      currentDisplayedData: '',
      showLoader: false,
      watchURL: true,

      selectionData: {
        type: '',
        data: null,
        error: false,
      },
      showSelectionLoader: false,
      isHoverMenuItem: false,
      lastRoute: {},
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
      queryParams: 'maps/queryParams',
    }),
    dim() {
      return this.showing2D ? '2d' : '3d';
    },
  },
  watch: {
    '$route.params': 'loadMapFromParams',
  },
  created() {
    // this.handleQueryParamsWatch = debounce(this.handleQueryParamsWatch, 100);
    // window.onpopstate = this.handleQueryParamsWatch();
    EventBus.$off('loadRNAComplete');
    EventBus.$on('loadRNAComplete', (isSuccess, errorMessage) => {
      if (!isSuccess) {
        this.showMessage(errorMessage);
        EventBus.$emit('unselectFirstTissue');
        EventBus.$emit('unselectSecondTissue');
      } else {
        this.showLoader = false;
      }
    });
  },
  async beforeMount() {
    this.$store.dispatch('maps/initFromQueryParams', this.$route.query);
    await this.getSubComptData(this.model);
  },
  methods: {
    loadMapFromParams() {
      if (false) { // request is invalid ?!?!?
        this.handleLoadComplete(false, `Invalid ID "${this.$route.params.map_id}"`);
      } else {
        this.loadMapErrorMessage = '';
      }
      this.showOverviewScreen = false;
    },
    toggleDataOverlayPanel() {
      this.$store.dispatch('maps/toggleDataOverlayPanelVisible');
      EventBus.$emit('recompute3DCanvasBounds');
    },
    handleLoadComplete(isSuccess, errorMessage) {
      if (!isSuccess) {
        this.selectionData.data = null;
        this.showMessage(errorMessage);
        this.currentDisplayedName = '';
        return;
      }
      this.showOverviewScreen = false;
      this.currentDisplayedName = this.requestedName;
      this.showLoader = false;
      this.$nextTick(() => {
        EventBus.$emit('reloadGeneExpressionData');
      });
    },
    showMessage(errorMessage) {
      this.loadMapErrorMessage = errorMessage;
      if (!this.loadMapErrorMessage) {
        this.loadMapErrorMessage = messages.unknownError;
      }
      this.showLoader = false;
    },
    async getSubComptData(model) {
      try {
        await this.$store.dispatch('maps/getMapsListing', model);

        if (!this.has2DCompartmentMaps && !this.has2DSubsystemMaps) {
          this.$store.dispatch('maps/setShowing2D', false);
        }
      } catch (error) {
        console.log(error);
        switch (error.status) {
          default:
            this.errorMessage = messages.unknownError;
        }
      }
    },
    endSelection(isSuccess) {
      this.showSelectionLoader = false;
      this.selectionData.error = !isSuccess;
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

  #iLoader {
    z-index: 10;
    position: absolute;
    background: black;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0.8;
    display: table;
    a {
      color: white;
      font-size: 5em;
      font-weight: 1000;
      display: table-cell;
      vertical-align: middle;
      background: black;
      border: 0;
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
