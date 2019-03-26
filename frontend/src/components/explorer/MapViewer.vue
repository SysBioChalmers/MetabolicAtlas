<template>
  <div id="mapViewer" class="extended-section">
    <div class="columns" id="iMainPanel" :class="{ 'is-fullheight' : errorMessage}">
      <template v-if="errorMessage">
        <div class="column">
          <br><br>
          <div class="columns">
            <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
              {{ errorMessage }}
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div id="iSideBar" class="column is-one-fifth-widescreen is-one-quarter-desktop is-one-quarter-tablet is-half-mobile is-fullheight">
          <div id="menu">
            <ul class="l0">
              <li>Compartments<span>&nbsp;&#9656;</span>
                <ul class="vhs l1">
                  <li @click="showMap()"><i>Clear selection</i></li>
                  <div v-show="!has2DCompartmentMaps || show3D">
                    <li v-for="cKey in Object.keys(mapsData3D.compartments).sort()" class="clickable"
                      @click="showMap(mapsData3D.compartments[cKey].name_id)">
                      {{ mapsData3D.compartments[cKey].name }} {{ mapsData3D.compartments[cKey].reaction_count != 0 ? `(${mapsData3D.compartments[cKey].reaction_count})` : '' }}
                    </li>
                  </div>
                  <div v-show="has2DCompartmentMaps && show2D">
                    <li v-for="cKey in Object.keys(mapsData2D.compartments).sort()" class="clickable"
                      :class="{ 'disable' : !mapsData2D.compartments[cKey].sha }" @click="showMap(mapsData2D.compartments[cKey].name_id)">
                      {{ mapsData2D.compartments[cKey].name }} {{ mapsData2D.compartments[cKey].reaction_count != 0 ? `(${mapsData2D.compartments[cKey].reaction_count})` : '' }}
                    </li>
                  </div>
                </ul>
              </li>
              <li>Subsystems<span>&nbsp;&#9656;</span>
                <ul class="vhs l1">
                  <li @click="showMap()"><i>Clear selection</i></li>
                  <div v-show="!has2DSubsystemMaps || show3D">
                    <li v-for="sKey in Object.keys(mapsData3D.subsystems).sort()" class="clickable"
                      @click="showMap(mapsData3D.subsystems[sKey].name_id, 'subsystem')">
                        {{ mapsData3D.subsystems[sKey].name }} {{ mapsData3D.subsystems[sKey].reaction_count != 0 ? `(${mapsData3D.subsystems[sKey].reaction_count})` : '' }}
                    </li>
                  </div>
                  <div v-show="has2DSubsystemMaps && mapsData2D.subsystems">
                    <li v-for="sKey in Object.keys(mapsData2D.subsystems).sort()" class="clickable"
                      v-if="mapsData2D.subsystems[sKey].name_id && mapsData2D.subsystems[sKey].sha" @click="showMap(mapsData2D.subsystems[sKey].name_id, 'subsystem')">
                        {{ mapsData2D.subsystems[sKey].name }} {{ mapsData2D.subsystems[sKey].reaction_count != 0 ? `(${mapsData2D.subsystems[sKey].reaction_count})` : '' }}
                    </li>
                    <li v-else class="disable">
                       {{ mapsData2D.subsystems[sKey].name }}
                    </li>
                  </div>
                </ul>
              </li>
              <li :class="{'clickable' : true, 'disable' : !currentDisplayedName || HPATissue.length === 0 }" >RNA levels from <i style="color: lightblue">proteinAtlas.org</i>
                <span v-show="HPATissue.length !== 0">&nbsp;&#9656;</span>
                <ul class="vhs l1">
                  <li v-show="HPATissue.length !== 0" @click="loadHPARNAlevels('None')"><i>Clear selection</i></li>
                  <li v-for="tissue in HPATissue" class="clickable is-capitalized" @click="loadHPARNAlevels(tissue)">
                    {{ tissue }}
                  </li>
                </ul>
              </li>
            </ul>
          </div>
          <sidebar-data-panels
            :model="model"
            :dim="show2D ? '2d' : '3d'"
            :tissue="loadedTissue"
            :mapType="currentDisplayedType"
            :mapName="currentDisplayedName"
            :mapsData="show2D ? mapsData2D : mapsData3D"
            :selectionData="selectionData"
            :loading="showSelectionLoader">
          </sidebar-data-panels>
        </div>
        <div v-show="overviewScreen" class="column">
          <p class="is-size-5">Load a map from the menu</p>
        </div>
        <div id="graphframe" v-show="!overviewScreen" class="column is-unselectable">
          <div class="is-fullheight">
            <svgmap v-show="!overviewScreen && show2D" :model="model" :mapsData="mapsData2D"
              @loadComplete="handleLoadComplete"
              @loading="showLoader=true">
            </svgmap>
            <d3dforce v-show="!overviewScreen && show3D" :model="model"
              @loadComplete="handleLoadComplete"
              @loading="showLoader=true">
            </d3dforce>
          </div>
          <div id="iLoader" class="loading" v-show="showLoader">
            <a class="button is-loading"></a>
          </div>
          <div id="iSwitch" v-show="!overviewScreen" class="overlay">
            <span class="button" @click="switchDimension" :disabled="disabled2D && show3D">
              Switch to&nbsp;<b>{{ show3D ? '2D' : '3D' }}</b>
            </span>
          </div>
          <transition name="slide-fade">
            <article id="errorBar" class="message is-danger" v-if="loadErrorMesssage">
              <div class="message-header">
                <i class="fa fa-warning"></i>
              </div>
              <div class="message-body">
                <h5 class="title is-5">{{ loadErrorMesssage }}</h5>
              </div>
            </article>
          </transition>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import $ from 'jquery';
import axios from 'axios';
import SidebarDataPanels from 'components/explorer/mapViewer/SidebarDataPanels';
import Svgmap from 'components/explorer/mapViewer/Svgmap';
import D3dforce from 'components/explorer/mapViewer/D3dforce';
import { default as EventBus } from '../../event-bus';
import { default as messages } from '../../helpers/messages';

export default {
  name: 'map-viewer',
  props: ['model'],
  components: {
    SidebarDataPanels,
    Svgmap,
    D3dforce,
  },
  data() {
    return {
      errorMessage: '',
      loadErrorMesssage: '',
      overviewScreen: true,
      show2D: true,
      show3D: false,
      disabled2D: false,
      requestedType: '',
      requestedName: '',
      currentDisplayedType: '',
      currentDisplayedName: '',
      has2DCompartmentMaps: false,
      has2DSubsystemMaps: false,
      showLoader: false,

      mapsData2D: {
        compartments: {},
        subsystems: {},
      },
      mapsData3D: {
        compartments: {},
        subsystems: {},
      },

      selectionData: {
        type: '',
        data: null,
        error: false,
      },
      showSelectionLoader: false,
      isHoverMenuItem: false,

      HPATissue: [],
      requestedTissue: '',
      loadedTissue: '',
      messages,
    };
  },
  computed: {
    activeSwitch() {
      return !this.showLoader;
    },
  },
  created() {
    EventBus.$off('showAction');
    EventBus.$off('updatePanelSelectionData');
    EventBus.$off('unSelectedElement');
    EventBus.$off('startSelectedElement');
    EventBus.$off('endSelectedElement');
    EventBus.$off('loadRNAComplete');

    EventBus.$on('showAction', (type, name, ids, forceReload) => {
      // console.log(`showAction ${type} ${name} ${ids} ${forceReload}`);
      if (this.showLoader) {
        return;
      }
      if (!this.checkValidRequest(type, name)) {
        this.handleLoadComplete(false, messages.mapNotFound);
        return;
      }
      if (this.show3D) {
        EventBus.$emit('show3Dnetwork', type, name);
      } else {
        EventBus.$emit('showSVGmap', type, name, ids, forceReload);
      }
    });

    EventBus.$on('updatePanelSelectionData', (data) => {
      this.selectionData = data;
    });
    EventBus.$on('unSelectedElement', () => {
      this.selectionData.error = false;
      this.selectionData.data = null;
    });
    EventBus.$on('startSelectedElement', () => {
      this.showSelectionLoader = true;
    });
    EventBus.$on('endSelectedElement', (isSuccess) => {
      this.showSelectionLoader = false;
      this.selectionData.error = !isSuccess;
      // this.showSelectedElementPanelError = !isSuccess;
    });
    EventBus.$on('loadRNAComplete', (isSuccess, errorMessage) => {
      if (!isSuccess) {
        // show error
        this.loadErrorMesssage = errorMessage;
        if (!this.loadErrorMesssage) {
          this.loadErrorMesssage = messages.unknownError;
        }
        this.showLoader = false;
        this.loadedTissue = '';
        this.requestedTissue = '';
        setTimeout(() => {
          this.loadErrorMesssage = '';
        }, 3000);
        return;
      }
      this.loadedTissue = this.requestedTissue;
      this.showLoader = false;
    });
  },
  beforeMount() {
    this.setup();
  },
  mounted() {
    // menu
    const self = this;
    $('#menu').on('mouseenter', 'ul.l0 > li:has(ul)', function f() {
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
  },
  methods: {
    setup() {
      if (!this.model || this.model.database_name !== this.$route.params.model) {
        EventBus.$emit('modelSelected', '');
        this.errorMessage = `Error: ${messages.modelNotFound}`;
        return;
      }
      this.getSubComptData(this.model);
      this.getHPATissue(this.model);
    },
    hideDropleftMenus() {
      $('#menu ul.l1, #menu ul.l2').hide();
    },
    switchDimension() {
      if (!this.activeSwitch || this.disabled2D) {
        return;
      }
      this.show3D = !this.show3D;
      this.show2D = !this.show2D;
      this.selectedElement = null;
      this.requestedTissue = '';
      this.loadedTissue = '';
      if (!this.currentDisplayedType || !this.currentDisplayedName) {
        return;
      }

      if (this.show3D) {
        EventBus.$emit('show3Dnetwork', this.currentDisplayedType, this.currentDisplayedName);
      } else {
        EventBus.$emit('destroy3Dnetwork');
        EventBus.$emit('showSVGmap', this.currentDisplayedType, this.currentDisplayedName, [], true);
      }
    },
    handleLoadComplete(isSuccess, errorMessage) {
      if (!isSuccess) {
        this.selectionData.data = null;
        this.loadErrorMesssage = errorMessage;
        if (!this.loadErrorMesssage) {
          this.loadErrorMesssage = messages.unknownError;
        }
        this.showLoader = false;
        this.currentDisplayedType = '';
        this.currentDisplayedName = '';
        setTimeout(() => {
          this.loadErrorMesssage = '';
        }, 3000);
        return;
      }
      this.currentDisplayedType = this.requestedType;
      this.currentDisplayedName = this.requestedName;
      if (this.show2D) {
        EventBus.$emit('update3DLoadedComponent', null, null);
      }
      this.showLoader = false;
    },
    getSubComptData(model) {
      axios.get(`${model.database_name}/viewer/`)
      .then((response) => {
        this.mapsData3D.compartments = {};
        for (const c of response.data.compartment) {
          this.mapsData3D.compartments[c.name_id] = c;
        }
        this.mapsData2D.compartments = {};
        for (const c of response.data.compartmentsvg) {
          this.mapsData2D.compartments[c.name_id] = c;
        }
        this.has2DCompartmentMaps = Object.keys(this.mapsData2D.compartments).length !== 0;
        // this.mapsData2D.compartments.sort();
        this.mapsData3D.subsystems = {};
        for (const s of response.data.subsystem) {
          this.mapsData3D.subsystems[s.name_id] = s;
        }
        this.mapsData2D.subsystems = {};
        for (const s of response.data.subsystemsvg) {
          this.mapsData2D.subsystems[s.name_id] = s;
        }
        this.has2DSubsystemMaps = Object.keys(this.mapsData2D.subsystems).length !== 0;

        if (!this.has2DCompartmentMaps && !this.has2DSubsystemMaps) {
          this.disabled2D = true;
          this.show3D = true;
          this.show2D = false;
        }

        // load maps from url if contains map_id, the url is then cleaned of the id
        if (['viewerCompartment', 'viewerCompartmentRea', 'viewerSubsystem', 'viewerSubsystemRea'].includes(this.$route.name)) {
          const type = this.$route.name.includes('Compartment') ? 'compartment' : 'subsystem';
          const mapID = this.$route.params.id;
          const reactionID = this.$route.params.rid;
          if (!this.$route.query.dim) {
            this.show2D = false;
          } else {
            this.show2D = this.$route.query.dim === '2d' && !this.disabled2D;
          }
          this.show3D = !this.show2D;
          this.$nextTick(() => {
            EventBus.$emit('showAction', type, mapID, reactionID ? [reactionID] : [], false);
          });
        }
      })
      .catch((error) => {
        // console.log(error);
        switch (error.response.status) {
          default:
            this.errorMessage = messages.unknownError;
        }
      });
    },
    getHPATissue(model) {
      axios.get(`${model.database_name}/enzyme/hpa_tissue/`)
        .then((response) => {
          this.HPATissue = response.data;
        })
        .catch((error) => {
          switch (error.response.status) {
            default:
              this.loadErrorMesssage = messages.unknownError;
          }
        });
    },
    loadHPARNAlevels(tissue) {
      this.requestedTissue = tissue;
      if (this.requestedTissue === 'None') {
        this.requestedTissue = '';
        this.loadedTissue = '';
      }
      if (this.show2D) {
        EventBus.$emit('loadHPARNAlevels', tissue);
      }
    },
    checkValidRequest(displayType, displayName) {
      // correct special cytosol id, due to map split
      this.requestedType = displayType;
      this.requestedName = displayName;
      if (!displayType === 'compartment') {
        if (displayName === 'cytosol') {
          this.requestedName = 'cytosol_1';
        } else if (displayName === 'cytosol_1') {
          this.requestedName = 'cytosol';
        }
      }
      if (this.show2D) {
        if (displayType === 'compartment') {
          return this.requestedName in this.mapsData2D.compartments;
        }
        return this.requestedName in this.mapsData2D.subsystems;
      }
      if (displayType === 'compartment') {
        return this.requestedName in this.mapsData3D.compartments;
      }
      return this.requestedName in this.mapsData3D.subsystems;
    },
    showMap(compartmentOrSubsystemID, type = 'compartment') {
      this.selectionData.data = null;
      this.currentDisplayedName = null;
      this.currentDisplayedType = null;
      this.tissue = null;
      this.hideDropleftMenus();
      if (compartmentOrSubsystemID) {
        this.overviewScreen = false;
        EventBus.$emit('showAction', type, compartmentOrSubsystemID, [], false);
      } else {
        this.overviewScreen = true;
      }
    },
  },
};
</script>

<style lang="scss">

$navbar-height: 2.5rem;
$footer-height: 4.55rem;

#mapViewer {
  .is-fullheight {
    min-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    max-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    height: calc(100vh - #{$navbar-height} - #{$footer-height});
  }

  #iMainPanel {
    margin-bottom: 0;
  }

  #iSwitch {
    left: 2.25rem;
    top:  2.25rem;
  }

  #iSideBar {
    padding: 0.75rem 0 0 0.75rem;
    background: lightgray;
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

  .overlay {
    position: absolute;
    z-index: 10;
    padding: 15px;
    border-radius: 5px;
    background: rgba(22, 22, 22, 0.8);
  }

  #errorBar {
    z-index: 11;
    position: absolute;
    margin: 0;
    right: 0;
    bottom: 35px;
    border: 1px solid #FF4D4D;
  }

  .slide-fade-enter-active {
    transition: all .3s ease;
  }
  .slide-fade-leave-active {
    transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0);
  }
  .slide-fade-enter, .slide-fade-leave-active {
    transform: translateX(200px);
    opacity: 0;
  }
}

</style>
