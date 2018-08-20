<template>
  <div id="metabolicViewer">
    <div class="columns" id="iTopBar">
      <div class="column" id="iLogo">
        <svg-icon width="175" height="40" :glyph="Logo"></svg-icon>
      </div>
      <div class="column has-text-centered" id="iTitle">
        Metabolic Viewer of <span class="has-text-info">{{ model.name.toUpperCase() }}</span>
      </div>
      <div class="column">
        <button id="iHideBut" class="button is-dark is-pulled-right" @click="hideNetworkGraph()">Close</button>
      </div>
    </div>
<!--     <div class="columns">
      <div class="column is-2 has-text-centered" id="iSwitch">
        <div class="field">
          <label for="" @click="switch3Dimension(false)">2D Maps</label>
          <input id="dimSwitch" type="checkbox" name="dimSwitch"
           class="switch is-large is-rtl" :checked="!dim3D"
           :disabled="activeSwitch ? false : 'disabled'">
          <label for="" @click="switch3Dimension(null)"></label>
          <label for="" @click="switch3Dimension(true)">&nbsp;3D Force</label>
        </div>
      </div>
      <div class="column" id="iBarInfo" v-html="mapInfoString">
      </div>
    </div> -->
    <div class="columns" id="iMainPanel">
      <div class="column is-one-fifth" id="iSideBar">
        <div id="menu">
          <ul class="l0">
            <li @click="loadHPATissue" :class="{'clickable' : true, 'disable' : !currentDisplayedName }" >HPA RNA levels
              <span v-show="HPATissue.length !== 0">&nbsp;&#9656;</span>
              <ul class="vhs l1">
                <li v-show="HPATissue.length !== 0" @click="loadHPARNAlevels('None')">None</li>
                <li v-for="tissue in HPATissue" class="clickable" @click="loadHPARNAlevels(tissue)">
                  {{ tissue }}
                </li>
              </ul>
            </li>
            <li>Compartments<span>&nbsp;&#9656;</span>
              <ul class="vhs l1">
                <li v-for="comp in Object.keys(compartments)" class="clickable"
                @click="showCompartment(comp)">
                  {{ compartments[comp].name }}
<!--                    TODO ADD subystem for cytosol parts
 -->            </li>
              </ul>
            </li>
            <li>Subsystems<span>&nbsp;&#9656;</span>
              <ul class="l1">
                <li v-for="system in systemOrder">{{ system }}<span>&nbsp;&#9656;</span>
                  <ul class="l2" v-if="subsystems[system]">
                    <li v-for="subsystem in subsystems[system]" class="clickable" 
                      v-if="system !== 'Collection of reactions'" @click="showSubsystem(subsystem)">
                        {{ subsystem.name }}
                    </li>
                    <li v-else class="clickable disable">
                       {{ subsystem.name }}
                    </li>
                  </ul>
                </li>
              </ul>
            </li>
          </ul>
        </div>
        <div v-if="loadedTissue">
          <div class="has-text-centered has-text-weight-bold is-small">
            Current tissue: {{ loadedTissue }}
          </div>
          <div class="panel-block" v-html="getExpLvlLegend()" >
          </div>
        </div>
        <div id="iSelectedElementPanel">
          <div class="loading" v-show="showSelectedElementPanelLoader">
            <a class="button is-loading"></a>
          </div>
          <div v-show="!showSelectedElementPanelLoader">
            <div class="has-text-centered has-text-danger" v-if="showSelectedElementPanelError">
              {{ $t('unknownError') }}
            </div>
            <div v-else-if="currentDisplayedType">
              <div class="card">
                <header class="card-header">
                  <p class="card-header-title">
                    <template v-if="selectedElement">
                      {{ capitalize(selectedElementData.type) }}: {{ selectedElementData.id }}
                    </template>
                    <template v-else>
                      {{ capitalize(currentDisplayedType) }}: {{ currentDisplayedName }}
                    </template>
                  </p>
                </header>
                <div class="card-content">
                  <!-- TMP fix for overflow on side bar -->
                  <div class="content" style="max-height: 500px; overflow-y: auto;">
                    <template v-if="selectedElement">
                      <template v-if="['metabolite', 'enzyme', 'reaction'].includes(selectedElement)">
                        <p v-if="selectedElementData['rnaLvl'] != null">
                          <span class="hd">RNA&nbsp;level:</span><span>{{ selectedElementData['rnaLvl'] }}</span>
                        </p>
                        <template v-for="item in selectedElementDataKeys[model.id][selectedElement]"
                          v-if="selectedElementData[item.name] != null || item.name === 'external_ids'" >
                          <template v-if="item.name === 'external_ids'">
                            <span class="hd" v-html="capitalize(item.display || item.name) + ':'" 
                            v-if="hasExternalIDs(item.value)"></span>
                            <p v-if="hasExternalIDs(item.value)">
                              <template v-for="eid in item.value" v-if="selectedElementData[eid[1]] && selectedElementData[eid[2]]">
                                <span class="hd">{{ capitalize(eid[0]) }}:</span>
                                <span v-html="reformatStringToLink(selectedElementData[eid[1]], selectedElementData[eid[2]])"></span><br>
                              </template>
                            </p v-if="hasExternalIDs(item.value)">
                          </template>
                          <template v-else-if="['aliases', 'subsystem'].includes(item.name)">
                            <span class="hd">{{ capitalize(item.display || item.name) }}:</span><p>
                            <template v-for="s in selectedElementData[item.name].split('; ')">
                              &ndash;&nbsp;{{ s }}<br>
                            </template></p>
                          </template>
                          <template v-else-if="['reactants', 'products'].includes(item.name)">
                            <span class="hd">{{ capitalize(item.display || item.name) }}:</span><p>
                            <template v-for="s in selectedElementData[item.name]">
                              &ndash;&nbsp;{{ s.name }}<br>
                            </template></p>
                          </template>
                          <template v-else-if="item.name === 'equation'">
                            <p><span class="hd" v-html="capitalize(item.display || item.name) + ':'"></span><br>
                            <span v-html="chemicalReaction(selectedElementData[item.name], selectedElementData['is_reversible'])"></span></p>
                          </template>
                          <template v-else>
                            <p><span class="hd" v-html="capitalize(item.display || item.name) + ':'"></span>
                            {{ selectedElementData[item.name] }}</p>
                          </template>
                        </template>
                      </template>
                    </template>
                    <template v-else>
                      <template v-if="currentDisplayedType === 'compartment'">
                        <span class="hd"># reaction:</span> {{ compartmentStats[currentDisplayedName]['reaction_count'] }}<br>
                        <span class="hd"># metabolite:</span> {{ compartmentStats[currentDisplayedName]['metabolite_count'] }}<br>
                        <span class="hd"># enzyme:</span> {{ compartmentStats[currentDisplayedName]['enzyme_count'] }}<br>
                        <span class="hd"># subsystem:</span> {{ compartmentStats[currentDisplayedName]['subsystem_count'] }}
                      </template>
                      <template v-else>
                        <span class="hd">subsystem:</span>stats
                      </template>
                    </template>
                  </div>
                </div>
                <footer class="card-footer" 
                  v-if="['metabolite', 'enzyme', 'reaction'].includes(selectedElement) || currentDisplayedType === 'subsystem'">
                  <a  class="card-footer-item" @click="viewOnGemsExplorer()">View more on GEMs Explorer</a>
                </footer>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="column" id="graphframe">
        <div class="columns">
          <svgmap class="column" v-show="!dim3D"
          :model="model.id"
          @loadComplete="handleLoadComplete"
          @loading="showLoader=true"></svgmap>
          <d3dforce class="column" v-show="dim3D"
          :model="model.id"
          @loadComplete="handleLoadComplete"
          @loading="showLoader=true"></d3dforce>
        </div>
        <div id="iLoader" class="loading" v-show="showLoader">
          <a class="button is-loading"></a>
        </div>
      </div>
    </div>
    <transition name="slide-fade">
      <article id="errorBar" class="message is-danger" v-if="errorMessage">
        <div class="message-header">
          <i class="fa fa-warning"></i>
        </div>
        <div class="message-body">
          <h5 class="title is-5">{{ errorMessage }}</h5>
        </div>
      </article>
    </transition>
  </div>
</template>

<script>
import $ from 'jquery';
import axios from 'axios';
import Svgmap from './metabolicViewerComponents/Svgmap';
import D3dforce from './metabolicViewerComponents/D3dforce';
import SvgIcon from './SvgIcon';
import Logo from '../assets/logo.svg';
import { default as EventBus } from '../event-bus';
import { getCompartmentFromName } from '../helpers/compartment';
import { capitalize, reformatStringToLink } from '../helpers/utils';
import { chemicalReaction } from '../helpers/chemical-formatters';
import { getExpLvlLegend } from '../expression-sources/hpa';

export default {
  name: 'metabolic-viewer',
  components: {
    SvgIcon,
    Svgmap,
    D3dforce,
  },
  props: [
    'model', 'init',
  ],
  data() {
    return {
      Logo,
      errorMessage: '',
      dim3D: false,
      requestedType: '',
      requestedName: '',
      currentDisplayedType: '',
      currentDisplayedName: '',
      initialEmit: false,
      showLoader: false,

      compartments: {},
      compartmentStats: {},
      compartmentNameOrder: [
        'Endoplasmic reticulum',
        'Golgi apparatus',
        'Lysosome',
        'Mitochondria',
        'Nucleus',
        'Peroxisome',
        'Cytosol_1',
        'Cytosol_2',
        'Cytosol_3',
        'Cytosol_4',
        'Cytosol_5',
        'Cytosol_6',
      ],
      subsystems: {},
      currentubsystem: null,
      subsystemCount: 0,
      systemOrder: [
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

      selectedElement: null,
      showSelectedElementPanelLoader: false,
      showSelectedElementPanelError: false,
      selectedElementDataKeys: {
        hmr2: {
          metabolite: [
            { name: 'name' },
            { name: 'model_name', display: 'Model&nbsp;name' },
            { name: 'formula' },
            { name: 'compartment' },
            { name: 'aliases', display: 'Synonyms' },
            {
              name: 'external_ids',
              display: 'External&nbsp;IDs',
              value: [
                ['HMDB', 'hmdb_id', 'hmdb_link'],
                ['chebi', 'chebi_id', 'chebi_link'],
                ['mnxref', 'mnxref_id', 'mnxref_link'],
              ],
            },
          ],
          enzyme: [
            { name: 'gene_name', display: 'Gene&nbsp;name' },
            { name: 'gene_synonyms', display: 'Synonyms' },
            {
              name: 'external_ids',
              display: 'External&nbsp;IDs',
              value: [
                ['Uniprot', 'uniprot_id', 'uniprot_link'],
                ['NCBI', 'ncbi_id', 'ncbi_link'],
                ['Ensembl', 'id', 'name_link'],
              ],
            },
          ],
          reaction: [
            { name: 'equation' },
            { name: 'gene_rule', display: 'GPR' },
            { name: 'subsystem', display: 'Subsystems' },
            { name: 'reactants' },
            { name: 'products' },
          ],
        },
      },

      selectedElementData: {
        type: null,
        id: null,
        description: null,
        name: null,
        compartment: null, // mets only
        subsystems: null, // mets and reas only, ARRAY
        formula: null, // mets only
        equation: null, // reas only
        gpr: null, // reas only
        reversible: null, // reas only
        rna_level: null, // enz only
        synonyms: null, // mets and enz only
        external_ids: null, //[[source, ID, link],]
      },
      isHoverMenuItem: false,

      HPATissue: [],
      requestedTissue: '',
      loadedTissue: '',
    };
  },
  computed: {
    activeSwitch() {
      return ['compartment', 'subsystem'].includes(this.currentDisplayedType) && !this.showLoader;
    },
  },
  created() {
    this.loadCompartments();
    this.loadSubsystem();
    this.loadHPATissue();

    EventBus.$on('showAction', (type, name, secondaryName, ids, forceReload) => {
      console.log(`showAction ${type} ${name} ${secondaryName} ${ids}`);
      this.requestedType = type;
      if (type === 'subsystem') {
        this.requestedName = secondaryName;
      } else {
        this.requestedName = name;
      }
      if (this.dim3D) {
        if (['compartment', 'subsystem'].includes(type)) {
          EventBus.$emit('show3Dnetwork', type, this.requestedName);
        } else {
          // show error
        }
      } else {
        EventBus.$emit('showSVGmap', type, name, ids, forceReload);
      }
    });

    EventBus.$on('updatePanelSelectionData', (data) => {
      this.selectedElement = data.type;
      this.selectedElementData = data;
    });
    EventBus.$on('unSelectedElement', () => {
      this.selectedElement = null;
      this.selectedElementData = null;
    });
    EventBus.$on('startSelectedElement', () => {
      this.showSelectedElementPanelLoader = true;
    });
    EventBus.$on('endSelectedElement', (isSuccess) => {
      this.showSelectedElementPanelLoader = false;
      this.showSelectedElementPanelError = !isSuccess;
    });
    EventBus.$on('loadRNAComplete', (isSuccess, errorMessage) => {
      if (!isSuccess) {
        // show error
        this.errorMessage = errorMessage;
        if (!this.errorMessage) {
          this.errorMessage = this.$t('unknownError');
        }
        this.showLoader = false;
        this.loadedTissue = '';
        this.requestedTissue = '';
        setTimeout(() => {
          this.errorMessage = '';
        }, 3000);
        return;
      }
      this.loadedTissue = this.requestedTissue;
      this.showLoader = false;
    });
  },
  mounted() {
    if (false && this.currentDisplayedType === 'wholemap' &&
     !this.initialEmit) {
      EventBus.$emit('showSVGmap', 'wholemap', null, [], false);
      this.initialEmit = true;
    }

    // menu
    const self = this;
    $('#menu').on('mouseenter', 'ul.l0 > li:has(ul)', function () {
      $('#menu ul.l1, #menu ul.l2').hide();
      $(this).find('ul').first().show();
      self.isHoverMenuItem = true;
    });
    $('#menu').on('mouseleave', 'ul.l0 > li:has(ul)', function () {
      self.isHoverMenuItem = false;
      $(this).find('ul').first().delay(500)
        .queue(function () {
          if (!self.isHoverMenuItem) {
            $(this).hide(0);
          }
          $(this).dequeue();
        });
    });
    $('#menu').on('mouseenter', 'ul.l1 > li:has(ul)', function () {
      $('#menu ul.l2').hide();
      $(this).find('ul').first().show();
      self.isHoverMenuItem = true;
    });
  },
  methods: {
    hasExternalIDs(keys) {
      for (const eid of keys) {
        if (this.selectedElementData[eid[1]] && this.selectedElementData[eid[2]]) {
          return true;
        }
      }
      return false;
    },
    viewOnGemsExplorer() {
      if (this.currentDisplayedType === 'subsystem') {
        EventBus.$emit('updateSelTab', this.currentDisplayedType, this.currentDisplayedName);
      } else {
        EventBus.$emit('updateSelTab', this.selectedElementData.type, this.selectedElementData.id);
      }
      this.hideNetworkGraph();
    },
    hideNetworkGraph() {
      EventBus.$emit('toggleNetworkGraph');
    },
    // globalMapSelected() {
    //   this.accordionLevelSelected = 'wholemap';
    //   this.switch3Dimension(false);
    //   EventBus.$emit('showSVGmap', 'wholemap', null, []);
    // },
    switch3Dimension(b) {
      if (!this.activeSwitch) {
        return;
      }
      if (this.dim3D) {
        this.dim3D = b;
      } else if (this.currentDisplayedType !== 'wholemap') {
        if (b !== null) {
          this.dim3D = b;
        } else {
          this.dim3D = !this.dim3D;
        }
      }
      if (this.dim3D) {
        EventBus.$emit('show3Dnetwork', this.currentDisplayedType, this.currentDisplayedName);
      } else {
        EventBus.$emit('destroy3Dnetwork');
        EventBus.$emit('showSVGmap', this.currentDisplayedType, this.currentDisplayedName, [], true);
      }
    },
    handleLoadComplete(isSuccess, errorMessage) {
      console.log(`${isSuccess} ${errorMessage}`);
      if (!isSuccess) {
        // show error
        this.errorMessage = errorMessage;
        if (!this.errorMessage) {
          this.errorMessage = this.$t('unknownError');
        }
        this.showLoader = false;
        this.currentDisplayedType = '';
        this.currentDisplayedName = '';
        setTimeout(() => {
          this.errorMessage = '';
        }, 3000);
        return;
      }
      this.currentDisplayedType = this.requestedType;
      this.currentDisplayedName = this.requestedName;
      this.showLoader = false;
    },
    loadCompartments() {
      for (const Cname of this.compartmentNameOrder) {
        this.compartments[Cname] = getCompartmentFromName(Cname);
      }
      axios.get(`${this.model.id}/compartments_svg/`)
      .then((response) => {
        this.compartmentStats = {};
        for (const compInfo of response.data) {
          this.compartmentStats[compInfo.display_name] = compInfo;
        }
      })
      .catch((error) => {
        switch (error.response.status) {
          default:
            this.errorMessage = this.$t('unknownError');
        }
      });
    },
    loadSubsystem() {
      axios.get(`${this.model.id}/subsystems`)
        .then((response) => {
          const systems = response.data.reduce((subarray, el) => {
            const arr = subarray;
            if (!arr[el.system]) { arr[el.system] = []; }
            arr[el.system].push(el);
            return arr;
          }, {});
          this.subsystems = systems;
          this.subsystemCount = 0;
          for (const k of Object.keys(systems)) {
            this.subsystems[k] = this.subsystems[k].sort(
              (a, b) => {
                if (a.name > b.name) {
                  return 1;
                }
                return a.name < b.name ? -1 : 0;
              }
            );
            this.subsystemCount += systems[k].length;
          }
        })
        .catch((error) => {
          switch (error.response.status) {
            default:
              this.errorMessage = this.$t('unknownError');
          }
        });
    },
    loadHPATissue() {
      axios.get(`${this.model.id}/enzymes/hpa_tissue/`)
        .then((response) => {
          this.HPATissue = response.data;
        })
        .catch((error) => {
          switch (error.response.status) {
            default:
              this.errorMessage = this.$t('unknownError');
          }
        });
    },
    loadHPARNAlevels(tissue) {
      this.requestedTissue = tissue;
      if (this.requestedTissue === 'None') {
        this.requestedTissue = '';
        this.loadedTissue = '';
      }
      EventBus.$emit('loadHPARNAlevels', tissue);
    },
    showCompartment(compartment) {
      EventBus.$emit('requestViewer', 'compartment', compartment, '', []);
    },
    showSubsystem() {
      // if (this.selectedSystem !== 'Collection of reactions') {
      //   EventBus.$emit('showSubsystem', this.selectedSubsystem.name);
      // }
    },
    getCompartmentFromName,
    capitalize,
    reformatStringToLink,
    chemicalReaction,
    getExpLvlLegend,
  },
};
</script>

<style lang="scss">

#metabolicViewer {
  #iTopBar {
    height: 60px;

    border-bottom: 1px solid black;
    .column {
      padding-bottom: 0;
    }
  }

  #iLogo {
    margin-top: 5px;
  }

  #iTitle {
    font-size: 2em;
    font-style: bold;
  }

  #iHideBut {
    margin: 10px;
  }

  #iMainPanel {
    flex: 1;
  }

/*  #iSwitch {
    label {
      font-size: 1.5rem;
      cursor: pointer;
    }
  }*/

  #iSideBar {
    padding: 0;
    margin: 0;
    padding-left: 0.75rem;

    #iSelectedElementPanel {
      margin: 0.75rem;

      .content {
        span.hd {
          font-weight: bold;
          margin-right: 5px;
        }
      }
    }
  }

  #iLoader {
    z-index: 10;
    position: absolute;
    background: black;
    top: 0;
    left: 0;
    width: 100%;
    height: 90%;
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
    height: 100vh;
    padding: 0;
    margin: 0;
    border: 1px solid darkgray;
    > .columns {
      margin: 0;
      > .column {
        padding: 0;
      }
    }
  }

  #errorBar {
    position: absolute;
    margin: 0;
    right: 0;
    bottom: 0;
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

  #menu { width: auto; background: #4a4a4a; color: white; position: relative; font-size: 18px; }
  #menu ul {
    list-style: none;
    &.vhs, &.l2 {
      max-height: 75vh; overflow-y: auto;
    }
  }
  #menu li {
    padding: 17px 15px 17px 20px;
    border-bottom: 1px solid gray;
    border-left: 1px solid white;
    user-select: none;
    &:hover {
      background: #2a2a2a;
    }
    span {
      position: absolute;
      right: 10px;
    }
    &.clickable {
        cursor: pointer;
        &.disable {
          cursor: default;
          background: #4a4a4a;
          color: gray;
          pointer-events: none;
        }
    }
  }
  #menu ul.l1, #menu  ul.l2 {
    display: none;
    position: absolute; top: 0; left: 100%; width: 100%;
    background: #4a4a4a; z-index: 11;
    box-shadow: 5px 5px 5px #222222;
  }
}

</style>
