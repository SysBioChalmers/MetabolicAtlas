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
        <div id="iSideBar" class="column is-one-fifth is-fullheight">
          <div id="menu">
            <ul class="l0">
              <li>Compartments<span>&nbsp;&#9656;</span>
                <ul class="vhs l1">
                  <template v-if="!has2DCompartmentMaps || show3D">
                    <li v-for="id in compartmentOrder[model.database_name]" class="clickable" v-if="mapsData3D.compartments[id]"
                      @click="showCompartment(mapsData3D.compartments[id].name_id)">
                      {{ mapsData3D.compartments[id].name }} {{ mapsData3D.compartments[id].reaction_count != 0 ? `(${mapsData3D.compartments[id].reaction_count})` : '' }}
                    </li>
                  </template>
                  <template v-else-if="mapsData2D.compartments">
                    <li v-for="id in compartmentOrder[model.database_name]" class="clickable" v-if="mapsData2D.compartments[id]" :class="{ 'disable' : !mapsData2D.compartments[id].sha }"
                      @click="showCompartment(mapsData2D.compartments[id].name_id)">
                      {{ mapsData2D.compartments[id].name }} {{ mapsData2D.compartments[id].reaction_count != 0 ? `(${mapsData2D.compartments[id].reaction_count})` : '' }}
                    </li>
                  </template>
                </ul>
              </li>
              <li>Subsystems<span>&nbsp;&#9656;</span>
                <template v-if="Object.keys(mapsData3D.subsystems).length !== 1">
                  <ul class="l1">
                    <li v-for="system in systemOrder[model.database_name]">{{ system }}<span>&nbsp;&#9656;</span>
                      <ul class="l2" v-if="mapsData3D.subsystems[system]">
                        <template v-if="!has2DSubsystemMaps || show3D">
                          <li v-for="subsystem in mapsData3D.subsystems[system]" class="clickable"
                            v-if="system !== 'Collection of reactions' && mapsData3D.subsystems[system]" @click="showSubsystem(subsystem.name_id)">
                              {{ subsystem.name }} {{ mapsData3D.subsystems[subsystem.name_id].reaction_count != 0 ? `(${mapsData3D.subsystems[subsystem.name_id].reaction_count})` : '' }}
                          </li>
                          <li v-else class="clickable disable">
                             {{ subsystem.name }}
                          </li>
                        </template>
                        <template v-else-if="mapsData2D.subsystems">
                          <li v-for="subsystem in mapsData3D.subsystems[system]" class="clickable" :class="{ 'disable' : !mapsData2D.subsystems[subsystem.name_id].sha }"
                            v-if="system !== 'Collection of reactions' && mapsData2D.subsystems[subsystem.name_id]" @click="showSubsystem(subsystem.name_id)">
                              {{ subsystem.name }} {{ mapsData2D.subsystems[subsystem.name_id].reaction_count != 0 ? `(${mapsData2D.subsystems[subsystem.name_id].reaction_count})` : '' }}
                          </li>
                          <li v-else class="clickable disable">
                             {{ subsystem.name }}
                          </li>
                        </template>
                      </ul>
                    </li>
                  </ul>
                </template>
                <template v-else>
                  <!-- the model no do contains 'system' annoation for subsystems -->
                  <ul class="vhs l1" v-if="mapsData3D.subsystems['']">
                    <template v-if="!has2DSubsystemMaps || show3D">
                      <li v-for="subsystem in mapsData3D.subsystems['']" class="clickable"
                        @click="showSubsystem(subsystem.name_id)">
                          {{ subsystem.name }} {{ mapsData3D.subsystems[subsystem.name_id].reaction_count != 0 ? `(${mapsData3D.subsystems[subsystem.name_id].reaction_count})` : '' }}
                      </li>
                    </template>
                    <template v-else-if="mapsData2D.subsystems">
                      <li v-for="subsystem in mapsData3D.subsystems['']" class="clickable" :class="{ 'disable' : !mapsData2D.subsystems[subsystem.name_id].sha }"
                        v-if="mapsData2D.subsystems[subsystem.name_id]" @click="showSubsystem(subsystem.name_id)">
                          {{ subsystem.name }} {{ mapsData2D.subsystems[subsystem.name_id].reaction_count != 0 ? `(${mapsData2D.subsystems[subsystem.name_id].reaction_count})` : '' }}
                      </li>
                      <li v-else class="clickable disable">
                         {{ subsystem.name }}
                      </li>
                    </template>
                  </ul>
                </template>
              </li>
              <li :class="{'clickable' : true, 'disable' : !currentDisplayedName || HPATissue.length === 0 }" >RNA levels from <i style="color: lightblue">proteinAtlas.org</i>
                <span v-show="HPATissue.length !== 0">&nbsp;&#9656;</span>
                <ul class="vhs l1">
                  <li v-show="HPATissue.length !== 0" @click="loadHPARNAlevels('None')"><i>Clear selection</i></li>
                  <li v-for="tissue in HPATissue" class="clickable" @click="loadHPARNAlevels(tissue)">
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
            :loading="showSelectionLoader"></sidebar-data-panels>
        </div>
        <div id="graphframe" class="column is-unselectable">
          <div class="is-fullheight">
            <svgmap v-show="show2D" :model="model" :mapsData="show2D ? mapsData2D : mapsData3D"
              @loadComplete="handleLoadComplete"
              @loading="showLoader=true">
            </svgmap>
            <d3dforce v-show="show3D" :model="model"
              @loadComplete="handleLoadComplete"
              @loading="showLoader=true">
            </d3dforce>
          </div>
          <div id="iLoader" class="loading" v-show="showLoader">
            <a class="button is-loading"></a>
          </div>
          <div id="iSwitch" class="overlay">
            <span class="button" @click="switchDimension" :disabled="disabled2D && show3D">
              {{ show3D ? '2D' : '3D' }}
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

      compartmentOrder: {
        hmr2: [
          'endoplasmic_reticulum',
          'golgi',
          'lysosome',
          'mitochondria',
          'nucleus',
          'peroxisome',
          'cytosol',
          'cytosol_1',
          'cytosol_2',
          'cytosol_3',
          'cytosol_4',
          'cytosol_5',
          'cytosol_6',
        ],
        yeast: [
          'cytoplasm',
          'cell_envelope',
          'extracellular',
          'endoplasmic_reticulum',
          'endoplasmic_reticulum_membrane',
          'golgi',
          'golgi_membrane',
          'lipid_particle',
          'mitochondrion',
          'mitochondrial_membrane',
          'nucleus',
          'peroxisome',
          'vacuole',
          'vacuolar_membrane',
        ],
      },
      systemOrder: {
        hmr2: [
          'Cholesterol biosynthesis',
          'Carnitine shuttle',
          'Glycosphingolipid biosynthesis/metabolism',
          'Amino Acid metabolism',
          'Fatty acid',
          'Vitamin metabolism',
          'Other metabolism',
          'Other',
          'Collection of reactions',
        ],
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
      this.selectionData.data = null;
      if (!isSuccess) {
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
    showCompartment(compartment) {
      this.selectionData.data = null;
      this.hideDropleftMenus();
      EventBus.$emit('showAction', 'compartment', compartment, [], false);
    },
    showSubsystem(subsystem) {
      this.selectionData.data = null;
      this.hideDropleftMenus();
      EventBus.$emit('showAction', 'subsystem', subsystem, [], false);
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
    right: 2.25rem;
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
