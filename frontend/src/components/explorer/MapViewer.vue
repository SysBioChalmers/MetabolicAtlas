<template>
  <div id="mapViewer" class="extended-section">
    <div class="columns" id="iMainPanel">
      <div class="column is-one-fifth is-fullheight" id="iSideBar">
        <div id="menu">
          <ul class="l0">
            <li :class="{'clickable' : true, 'disable' : !currentDisplayedName }" >RNA levels from <i style="color: lightblue">proteinAtlas.org</i>
              <span v-show="HPATissue.length !== 0">&nbsp;&#9656;</span>
              <ul class="vhs l1">
                <li v-show="HPATissue.length !== 0" @click="loadHPARNAlevels('None')">None</li>
                <li v-for="tissue in HPATissue" class="clickable" @click="loadHPARNAlevels(tissue)">
                  {{ tissue }}
                </li>
              </ul>
            </li>
            <li>Compartments<span>&nbsp;&#9656;</span>
              <ul class="vhs l1" v-if="Object.keys(compartmentsSVG).length !== 0">
                <li v-for="id in compartmentOrder" class="clickable" v-if="compartmentsSVG[id]" :class="{ 'disable' : false }"
                  @click="showCompartment(id)">
                  {{ compartmentsSVG[id].display_name }}
<!--                    TODO ADD subsystem for cytosol parts
 -->            </li>
              </ul>
            </li>
            <li>Subsystems<span>&nbsp;&#9656;</span>
              <ul class="l1">
                <li v-for="system in systemOrder">{{ system }}<span>&nbsp;&#9656;</span>
                  <ul class="l2" v-if="subsystems[system]">
                    <li v-for="subsystem in subsystems[system]" class="clickable" :class="{ 'disable' : !subsystemsSVG[subsystem.id].sha }"
                      v-if="system !== 'Collection of reactions' && subsystemsSVG[subsystem.id]" @click="showSubsystem(subsystem.id)">
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
        <div class="column" v-if="loadedTissue && show2D">
          <div class="has-text-centered has-text-weight-bold is-small">
            <p>Selected tissue: {{ loadedTissue }}</p>
          </div>
          <div v-html="getExpLvlLegend()">
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
                    <template v-else-if="currentDisplayedType === 'compartment'">
                      {{ capitalize(currentDisplayedType) }}: {{ compartmentsSVG[currentDisplayedName].display_name }}
                    </template>
                    <template v-else-if="currentDisplayedType === 'subsystem'">
                      {{ capitalize(currentDisplayedType) }}: {{ subsystemsSVG[currentDisplayedName].display_name }}
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
                        <template v-for="item in selectedElementDataKeys[model][selectedElement]"
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
<!--                         On map:<br>
                        <span class="hd"># reactions:</span> {{ compartmentsSVG[currentDisplayedName]['reaction_count'] }}<br>
                        <span class="hd"># metabolites:</span> {{ compartmentsSVG[currentDisplayedName]['metabolite_count'] }}<br>
                        <span class="hd"># enzymes:</span> {{ compartmentsSVG[currentDisplayedName]['enzyme_count'] }}<br>
                        <span class="hd"># subsystems:</span> {{ compartmentsSVG[currentDisplayedName]['subsystem_count'] }}<br>
                        <br>On model:<br> -->
                        <span class="hd"># reactions:</span> {{ compartments[compartmentsSVG[currentDisplayedName].compartment]['reaction_count'] }}<br>
                        <span class="hd"># metabolites:</span> {{ compartments[compartmentsSVG[currentDisplayedName].compartment]['metabolite_count'] }}<br>
                        <span class="hd"># enzymes:</span> {{ compartments[compartmentsSVG[currentDisplayedName].compartment]['enzyme_count'] }}<br>
                        <span class="hd"># subsystems:</span> {{ compartments[compartmentsSVG[currentDisplayedName].compartment]['subsystem_count'] }}<br>
                      </template>
                      <template v-else>
<!--                         On map:<br>
                        <span class="hd"># reactions:</span> {{ subsystemsSVG[currentDisplayedName]['reaction_count'] }}<br>
                        <span class="hd"># metabolites:</span> {{ subsystemsSVG[currentDisplayedName]['metabolite_count'] }}<br>
                        <span class="hd"># enzymes:</span> {{ subsystemsSVG[currentDisplayedName]['enzyme_count'] }}<br>
                        <br>On model:<br> -->
                        <span class="hd"># reactions:</span> {{ subsystemsStats[subsystemsSVG[currentDisplayedName].subsystem]['reaction_count'] }}<br>
                        <span class="hd"># metabolites:</span> {{ subsystemsStats[subsystemsSVG[currentDisplayedName].subsystem]['metabolite_count'] }}<br>
                        <span class="hd"># enzymes:</span> {{ subsystemsStats[subsystemsSVG[currentDisplayedName].subsystem]['enzyme_count'] }}<br>
                        <span class="hd"># compartments:</span> {{ subsystemsStats[subsystemsSVG[currentDisplayedName].subsystem]['compartment_count'] }}<br>
                      </template>
                    </template>
                  </div>
                </div>
                <footer class="card-footer" 
                  v-if="['metabolite', 'enzyme', 'reaction'].includes(selectedElement) || currentDisplayedType === 'subsystem'">
                  <a class="card-footer-item has has-text-centered" @click="viewOnGemBrowser()">View more on the Browser</a>
                </footer>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div id="graphframe" class="column">
        <div class="is-fullheight">
          <svgmap v-show="show2D"
          :model="model"
          @loadComplete="handleLoadComplete"
          @loading="showLoader=true"></svgmap>
          <d3dforce v-show="show3D"
          :model="model"
          @loadComplete="handleLoadComplete"
          @loading="showLoader=true"></d3dforce>
        </div>
        <div id="iLoader" class="loading" v-show="showLoader">
          <a class="button is-loading"></a>
        </div>
        <div id="iSwitch" class="overlay">
          <span class="button" @click="switchDimension">
            {{ show3D ? '2D' : "3D" }}
          </span>
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
    </div>

  </div>
</template>

<script>
import $ from 'jquery';
import axios from 'axios';
import Svgmap from 'components/explorer/mapViewer/Svgmap';
import D3dforce from 'components/explorer/mapViewer/D3dforce';
import Logo from '../../assets/logo.svg';
import { default as EventBus } from '../../event-bus';
import { capitalize, reformatStringToLink } from '../../helpers/utils';
import { chemicalReaction } from '../../helpers/chemical-formatters';
import { getExpLvlLegend } from '../../expression-sources/hpa';

export default {
  name: 'map-viewer',
  components: {
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
      show2D: true,
      show3D: false,
      requestedType: '',
      requestedName: '',
      currentDisplayedType: '',
      currentDisplayedName: '',
      initialEmit: false,
      showLoader: false,

      compartments: {},
      compartmentsSVG: {},
      compartmentOrder: [
        'er',
        'golgi',
        'lysosome',
        'mitochondria',
        'nucleus',
        'peroxisome',
        'cytosol_1',
        'cytosol_2',
        'cytosol_3',
        'cytosol_4',
        'cytosol_5',
        'cytosol_6',
      ],
      subsystems: {},
      subsystemsStats: {},
      subsystemsSVG: {},
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
      return !this.showLoader;
    },
  },
  created() {
    this.loadSubComptData();
    this.loadHPATissue();

    EventBus.$on('showAction', (type, name, ids, forceReload) => {
      // console.log(`showAction ${type} ${name} ${secondaryName} ${ids}`);
      if (this.showLoader) {
        return;
      }
      this.requestedType = type;
      this.requestedName = name;
      if (this.show3D) {
        EventBus.$emit('show3Dnetwork', type, name);
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
    // if (false && this.currentDisplayedType === 'wholemap' &&
    //  !this.initialEmit) {
    //   EventBus.$emit('showSVGmap', 'wholemap', null, [], false);
    //   this.initialEmit = true;
    // }

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
    hideDropleftMenus() {
      $('#menu ul.l1, #menu ul.l2').hide();
    },
    hasExternalIDs(keys) {
      for (const eid of keys) {
        if (this.selectedElementData[eid[1]] && this.selectedElementData[eid[2]]) {
          return true;
        }
      }
      return false;
    },
    viewOnGemBrowser() {
      if (this.currentDisplayedType === 'subsystem') {
        EventBus.$emit('navigateTo', 'GEMBrowser', this.currentDisplayedType, this.subsystemsSVG[this.currentDisplayedName].subsystem);
      } else {
        EventBus.$emit('navigateTo', 'GEMBrowser', this.selectedElementData.type, this.selectedElementData.id);
      }
    },
    // globalMapSelected() {
    //   this.accordionLevelSelected = 'wholemap';
    //   this.switch3Dimension(false);
    //   EventBus.$emit('showSVGmap', 'wholemap', null, []);
    // },
    switchDimension() {
      if (!this.activeSwitch) {
        return;
      }
      if (!this.currentDisplayedType || !this.currentDisplayedName) {
        return;
      }
      this.show3D = !this.show3D;
      this.show2D = !this.show2D;
      this.selectedElement = null;
      this.requestedTissue = '';
      this.loadedTissue = '';
      if (this.show3D) {
        EventBus.$emit('show3Dnetwork', this.currentDisplayedType, this.currentDisplayedName);
      } else {
        EventBus.$emit('destroy3Dnetwork');
        EventBus.$emit('showSVGmap', this.currentDisplayedType, this.currentDisplayedName, [], true);
      }
    },
    handleLoadComplete(isSuccess, errorMessage) {
      // console.log(`${isSuccess} ${errorMessage}`);
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
      if (this.show2D) {
        EventBus.$emit('update3DLoadedComponent', null, null);
      }
      this.showLoader = false;
    },
    loadSubComptData() {
      axios.get(`${this.model}/viewer/`)
      .then((response) => {
        this.compartments = {};
        for (const c of response.data.compartment) {
          this.compartments[c.name] = c;
        }
        this.compartmentsSVG = {};
        for (const c of response.data.compartmentsvg) {
          this.compartmentsSVG[c.id] = c;
        }
        this.subsystemsStats = {};
        for (const s of response.data.subsystem) {
          this.subsystemsStats[s.name] = s;
        }
        this.subsystemsSVG = {};
        for (const s of response.data.subsystemsvg) {
          this.subsystemsSVG[s.id] = s;
          this.subsystemsStats[s.subsystem].id = s.id;
        }
        const systems = response.data.subsystem.reduce((subarray, el) => {
          const arr = subarray;
          if (!arr[el.system]) { arr[el.system] = []; }
          el.id = this.subsystemsStats[el.name].id; // eslint-disable-line no-param-reassign
          arr[el.system].push(el);
          return arr;
        }, {});
        this.subsystems = systems;
        for (const k of Object.keys(systems)) {
          this.subsystems[k] = this.subsystems[k].sort(
            (a, b) => {
              if (a.name > b.name) {
                return 1;
              }
              return a.name < b.name ? -1 : 0;
            }
          );
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
      axios.get(`${this.model}/enzymes/hpa_tissue/`)
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
      if (this.show2D) {
        EventBus.$emit('loadHPARNAlevels', tissue);
      }
    },
    showCompartment(compartment) {
      this.hideDropleftMenus();
      EventBus.$emit('showAction', 'compartment', compartment, [], false);
    },
    showSubsystem(subsystem) {
      this.hideDropleftMenus();
      EventBus.$emit('showAction', 'subsystem', subsystem, [], false);
    },
    capitalize,
    reformatStringToLink,
    chemicalReaction,
    getExpLvlLegend,
  },
};
</script>

<style lang="scss">

$navbar-height: 6.5rem;
$footer-height: 9.8rem;

#mapViewer {
  border: 1px solid black;
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

  .is-fullheight {
    min-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    max-height: calc(100vh - #{$navbar-height} - #{$footer-height});
    height: calc(100vh - #{$navbar-height} - #{$footer-height});
    .column {
      overflow-y: auto;
    }
  }

  #iMainPanel {
    margin-bottom: 0;
  }

  #iSwitch {
    right: 2.25rem;
    top:  2.25rem;
  }

  #iSideBar {
    padding: 0;
    margin: 0;
    padding-left: 0.75rem;
    padding-top: 0.75rem;
    height: 100%;
    background: lightgray;

    #iSelectedElementPanel {
      margin: 0.75rem;

      .content {
        overflow-y: auto;
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
    border: 1px solid darkgray;
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

  #menu { width: auto; background: #4a4a4a; color: white; position: relative; font-size: 16px; }
  #menu ul {
    list-style: none;
    &.vhs, &.l2 {
      max-height: 65vh; overflow-y: auto;
    }
  }
  #menu li {
    padding: 17px 15px 17px 20px;
    border-bottom: 1px solid gray;
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
    border-left: 1px solid white;
    position: absolute; top: 0; left: 100%; width: 100%;
    background: #4a4a4a; z-index: 11;
    box-shadow: 5px 5px 5px #222222;
  }
}

</style>