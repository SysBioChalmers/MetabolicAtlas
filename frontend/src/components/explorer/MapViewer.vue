<template>
  <div id="mapViewer" class="extended-section">
    <div id="iMainPanel" class="columns">
      <template v-if="errorMessage">
        <div class="column">
          <div class="columns">
            <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
              <p>{{ errorMessage }}</p>
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div id="iSideBar" class="column is-one-fifth-widescreen is-one-quarter-desktop
        is-one-quarter-tablet is-half-mobile has-background-lightgray">
          <div id="menu">
            <ul class="l0">
              <li :title="`Select a ${dim.toUpperCase()} compartment network to show`">
                Compartments<span>&nbsp;&#9656;</span>
                <ul class="vhs l1" title="">
                  <li class="has-background-grey-dark clickable" @click="showMap()"><i>Clear selection</i></li>
                  <div v-if="!has2DCompartmentMaps || show3D">
                    <li v-for="cKey in Object.keys(mapsData3D.compartments).sort()" :key="cKey"
                        class="clickable"
                        :class="{'has-text-warning': cKey === currentDisplayedName }"
                        @click="showMap(mapsData3D.compartments[cKey].id, 'compartment', '3d')">
                      {{ mapsData3D.compartments[cKey].name }}
                    </li>
                  </div>
                  <div v-else>
                    <li v-for="cKey in Object.keys(mapsData2D.compartments).sort()" :key="cKey"
                        class="clickable"
                        :class="{ 'disable' : !mapsData2D.compartments[cKey].sha,
                                  'has-text-warning': cKey === currentDisplayedName }"
                        @click="showMap(mapsData2D.compartments[cKey].id, 'compartment', '2d')">
                      {{ mapsData2D.compartments[cKey].name }}
                    </li>
                  </div>
                </ul>
              </li>
              <li :title="`Select a ${dim.toUpperCase()} subsystem network to show`">
                Subsystems<span>&nbsp;&#9656;</span>
                <ul class="vhs l1" title="">
                  <li class="has-background-grey-dark clickable" @click="showMap()"><i>Clear selection</i></li>
                  <div v-if="!has2DSubsystemMaps || show3D">
                    <li v-for="sKey in Object.keys(mapsData3D.subsystems).sort()" :key="sKey"
                        class="clickable"
                        :class="{'has-text-warning': sKey === currentDisplayedName }"
                        @click="showMap(mapsData3D.subsystems[sKey].id, 'subsystem', '3d')">
                      {{ mapsData3D.subsystems[sKey].name }}
                    </li>
                  </div>
                  <div v-else>
                    <template v-for="sKey in Object.keys(mapsData2D.subsystems).sort()">
                      <template v-if="mapsData2D.subsystems[sKey].id && mapsData2D.subsystems[sKey].sha">
                        <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                        <li class="clickable" :class="{'has-text-warning': sKey === currentDisplayedName }"
                            @click="showMap(mapsData2D.subsystems[sKey].id, 'subsystem', '2d')">
                          {{ mapsData2D.subsystems[sKey].name }}
                        </li>
                      </template>
                      <template v-else>
                        <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                        <li class="disable">
                          {{ mapsData2D.subsystems[sKey].name }}
                        </li>
                      </template>
                    </template>
                  </div>
                </ul>
              </li>
            </ul>
          </div>
          <sidebar-data-panels
            :dim="dim"
            :map-type="currentDisplayedType"
            :map-name="currentDisplayedName"
            :maps-data="show2D ? mapsData2D : mapsData3D"
            :selection-data="selectionData"
            :loading="showSelectionLoader">
          </sidebar-data-panels>
        </div>
        <div v-show="showOverviewScreen" class="column">
          <p class="is-size-5 has-text-centered" style="padding: 10%;">
            Choose a compartment or subsystem map from the menu on the left
          </p>
        </div>
        <div v-show="!showOverviewScreen" id="graphframe" class="column is-unselectable">
          <template v-if="showMapViewer">
            <svgmap v-if="show2D" :maps-data="mapsData2D"
                    :requested-map-type="requestedType" :requested-map-name="requestedName"
                    @loadComplete="handleLoadComplete"
                    @loading="showLoader=true" @startSelection="showSelectionLoader=true" @endSelection="endSelection"
                    @unSelect="unSelect" @updatePanelSelectionData="updatePanelSelectionData">
            </svgmap>
            <d3dforce v-if="show3D"
                      :requested-map-type="requestedType" :requested-map-name="requestedName"
                      @loadComplete="handleLoadComplete"
                      @loading="showLoader=true" @startSelection="showSelectionLoader=true"
                      @endSelection="endSelection" @unSelect="unSelect"
                      @updatePanelSelectionData="updatePanelSelectionData">
            </d3dforce>
          </template>
          <div v-show="showLoader" id="iLoader" class="loading">
            <a class="button is-loading"></a>
          </div>
          <div id="iSwitch" class="overlay">
            <span class="button" :disabled="!activeSwitch"
                  :title="activeSwitch ? `Reload the current network in ${ show2D ? '3D' : '2D' }` : ''"
                  @click="switchDimension">
              <template v-if="activeSwitch">
                Switch to&nbsp;<b>{{ show2D ? '3D' : '2D' }}</b>
              </template>
              <template v-else>
                <template v-if="!disabled2D">
                  Switch to&nbsp;<b>{{ show2D ? '3D' : '2D' }}</b>
                </template>
                <template v-else>
                  Not available in 2D
                </template>
              </template>
            </span>
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
                     :map-type="currentDisplayedType"
                     :dim="dim" :map-name="currentDisplayedName">
        </DataOverlay>
      </template>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import $ from 'jquery';
import { debounce } from 'vue-debounce';
import SidebarDataPanels from '@/components/explorer/mapViewer/SidebarDataPanels';
import DataOverlay from '@/components/explorer/mapViewer/DataOverlay.vue';
import Svgmap from '@/components/explorer/mapViewer/Svgmap';
import D3dforce from '@/components/explorer/mapViewer/D3dforce';
import { default as EventBus } from '@/event-bus';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'MapViewer',
  components: {
    SidebarDataPanels,
    DataOverlay,
    Svgmap,
    D3dforce,
  },
  data() {
    return {
      errorMessage: '',
      loadMapErrorMessage: '',
      showOverviewScreen: true,
      requestedType: '',
      requestedName: '',
      currentDisplayedType: '',
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
      show2D: state => state.maps.show2D,
      dataOverlayPanelVisible: state => state.maps.dataOverlayPanelVisible,
    }),
    ...mapGetters({
      mapsData3D: 'maps/mapsData3D',
      mapsData2D: 'maps/mapsData2D',
      compartmentMapping: 'maps/compartmentMapping',
      has2DCompartmentMaps: 'maps/has2DCompartmentMaps',
      has2DSubsystemMaps: 'maps/has2DSubsystemMaps',
      show3D: 'maps/show3D',
      queryParams: 'maps/queryParams',
    }),
    activeSwitch() {
      return !this.showLoader && !this.disabled2D;
    },
    disabled2D() {
      if (this.show2D || !this.currentDisplayedName || this.showLoader) {
        return false;
      }
      if (!this.has2DCompartmentMaps && !this.has2DSubsystemMaps) {
        return true;
      }
      if (this.currentDisplayedType === 'compartment') {
        const altID = this.mapsData3D.compartments[this.currentDisplayedName].alternateDim;
        return !(altID in this.mapsData2D.compartments);
      }
      const altID = this.mapsData3D.subsystems[this.currentDisplayedName].alternateDim;
      return !(altID in this.mapsData2D.subsystems && this.mapsData2D.subsystems[altID].sha);
    },
    dim() {
      return this.show2D ? '2d' : '3d';
    },
    showMapViewer() {
      return this.$route.name === 'viewer';
    },
  },
  watch: {
    $route(to) {
      if (to.name === 'viewer' && to.query.dim && to.query.dim !== this.queryParams.dim) {
        this.$store.dispatch('maps/setShow2D', to.query.dim !== '3d');
      }
    },
    queryParams(newQuery, oldQuery) {
      this.handleQueryParamsWatch(newQuery, oldQuery);
    },
  },
  created() {
    this.handleQueryParamsWatch = debounce(this.handleQueryParamsWatch, 100);
    window.onpopstate = this.handleQueryParamsWatch();


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
  beforeUpdate() {
    if (!this.checkValidRequest(this.$route.params.type, this.$route.params.map_id) && this.showMapViewer) {
      this.handleLoadComplete(false, `Invalid map ID "${this.$route.params.map_id}"`);
    } else {
      this.loadMapErrorMessage = '';
    }
    this.showOverviewScreen = false; // to get the loader visible
  },
  mounted() {
    // menu
    const self = this;
    $('#menu').on('mouseenter', 'ul.l0 > li:has(ul)', function f() {
      if ($(this).hasClass('disable')) {
        return;
      }
      $('#menu ul.l1, #menu ul.l2').hide();
      $(this).find('ul').first().show();
      self.isHoverMenuItem = true;
    });
    $('#menu').on('mouseleave', 'ul.l0 > li:has(ul)', function f() {
      self.isHoverMenuItem = false;
      $(this).find('ul').first().delay(500)
        .queue(function ff() {
          if (!self.isHoverMenuItem) {
            $(this).hide(0);
          }
          $(this).dequeue();
        });
    });
    $('#menu').on('mouseenter', 'ul.l1 > li:has(ul)', function f() {
      $('#menu ul.l2').hide();
      $(this).find('ul').first().show();
      self.isHoverMenuItem = true;
    });

    $('#graphframe').on('click', () => {
      $('#menu ul.l1, #menu ul.l2').hide();
    });
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
    hideDropleftMenus() {
      $('#menu ul.l1, #menu ul.l2').hide();
    },
    toggleDataOverlayPanel() {
      this.$store.dispatch('maps/toggleDataOverlayPanelVisible');
      if (this.show3D) {
        // fix the 3D canvas size when open/close dataOverlay
        EventBus.$emit('recompute3DCanvasBounds');
      }
    },
    switchDimension() {
      if (!this.activeSwitch || !this.currentDisplayedType || !this.currentDisplayedName) {
        return;
      }

      if (!this.checkValidRequest(this.currentDisplayedType, this.currentDisplayedName)) {
        this.showMessage(`Invalid map ID "${this.currentDisplayedName}"`);
        return;
      }

      this.$store.dispatch('maps/toggleShow2D');
    },
    handleLoadComplete(isSuccess, errorMessage) {
      if (!isSuccess) {
        this.selectionData.data = null;
        this.showMessage(errorMessage);
        this.currentDisplayedType = '';
        this.currentDisplayedName = '';
        return;
      }
      this.showOverviewScreen = false;
      this.currentDisplayedType = this.requestedType;
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
          this.$store.dispatch('maps/setShow2D', false);
        }
      } catch (error) {
        switch (error.status) {
          default:
            this.errorMessage = messages.unknownError;
        }
      }
    },
    checkValidRequest(displayType, displayName) {
      this.requestedType = displayType;
      this.requestedName = displayName;
      if (this.show2D) {
        if (displayType === 'compartment') {
          if (displayName in this.compartmentMapping.dim3D) {
            this.requestedName = this.compartmentMapping.dim3D[displayName];
          }
          return this.requestedName in this.mapsData2D.compartments;
        }
        return this.requestedName in this.mapsData2D.subsystems
         && this.mapsData2D.subsystems[this.requestedName].sha;
      }
      if (displayType === 'compartment') {
        if (displayName in this.compartmentMapping.dim2D) {
          this.requestedName = this.compartmentMapping.dim2D[displayName];
        }
        return this.requestedName in this.mapsData3D.compartments;
      }
      return this.requestedName in this.mapsData3D.subsystems;
    },
    showMap(compartmentOrSubsystemID, type, dim) {
      if (compartmentOrSubsystemID === this.currentDisplayedName && type === this.currentDisplayedType) {
        this.hideDropleftMenus();
        return;
      }

      this.selectionData.data = null;
      this.hideDropleftMenus();

      if (dim) {
        this.$store.dispatch('maps/setShow2D', dim !== '3d');
      }

      if (compartmentOrSubsystemID) {
        this.$store.dispatch('maps/resetParamsExcept', ['dim', 'panel']);
        this.$router.push({
          name: 'viewer',
          params: { model: this.model.database_name, type, map_id: compartmentOrSubsystemID },
        }).catch(() => {});
      } else {
        this.currentDisplayedType = '';
        this.currentDisplayedName = '';
        this.showOverviewScreen = true;
        this.$store.dispatch('maps/resetParamsExcept', ['dim']);
        this.$router.push({ name: 'viewerRoot', params: { model: this.model.database_name } }).catch(() => {});
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
  #menu {
    background: $primary;
    color: $white;
    position: relative;
    font-size: 16px;
    ul {
      list-style: none;
      &.vhs, &.l2 {
        max-height: 65vh;
        overflow-y: auto;
      }
    }

    ul.l1, ul.l2 {
      display: none;
      border-left: 1px solid white;
      position: absolute;
      top: 0;
      left: 100%;
      width: 100%;
      background: $primary;
      z-index: 11;
      box-shadow: 5px 5px 5px #222222;
    }

    li {
      padding: 17px 15px 17px 20px;
      border-bottom: 1px solid $grey-lighter;
      user-select: none;
      &:hover {
        background: $primary-light;
      }
      span {
        position: absolute;
        right: 10px;
      }
      &.disable {
        cursor: not-allowed;
        background: $primary;
        color: $grey;
      }
    }
  }

  #iMainPanel {
    margin-bottom: 0;
    min-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    max-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    height: calc(100vh - #{$navbar-height} - #{$footer-height});
  }

  #iSwitch {
    left: 2.25rem;
    top:  2.25rem;
  }

  #iSideBar {
    padding: 0.75rem 0 0 0.75rem;
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
