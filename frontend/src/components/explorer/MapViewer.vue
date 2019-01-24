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
        <div class="column is-one-fifth is-fullheight" id="iSideBar">
          <div id="menu">
            <ul class="l0">
              <li :class="{'clickable' : true, 'disable' : !currentDisplayedName || HPATissue.length === 0 }" >RNA levels from <i style="color: lightblue">proteinAtlas.org</i>
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
                  <template v-if="!has2DCompartmentMaps || show3D">
                    <li v-for="id in compartmentOrder[model]" class="clickable" v-if="compartments[id]"
                      @click="showCompartment(compartments[id].name_id)">
                      {{ compartments[id].name }} {{ compartments[id].reaction_count != 0 ? `(${compartments[id].reaction_count})` : '' }}
                    </li>
                  </template>
                  <template v-else-if="compartmentsSVG">
                    <li v-for="id in compartmentOrder[model]" class="clickable" v-if="compartmentsSVG[id]" :class="{ 'disable' : !compartmentsSVG[id].sha }"
                      @click="showCompartment(compartmentsSVG[id].name_id)">
                      {{ compartmentsSVG[id].name }} {{ compartmentsSVG[id].reaction_count != 0 ? `(${compartmentsSVG[id].reaction_count})` : '' }}
                    </li>
                  </template>
                </ul>
              </li>
              <li>Subsystems<span>&nbsp;&#9656;</span>
                <template v-if="Object.keys(subsystems).length !== 1">
                  <ul class="l1">
                    <li v-for="system in systemOrder[model]">{{ system }}<span>&nbsp;&#9656;</span>
                      <ul class="l2" v-if="subsystems[system]">
                        <template v-if="!has2DSubsystemMaps || show3D">
                          <li v-for="subsystem in subsystems[system]" class="clickable"
                            v-if="system !== 'Collection of reactions' && subsystems[system]" @click="showSubsystem(subsystem.name_id)">
                              {{ subsystem.name }} {{ subsystems[subsystem.name_id].reaction_count != 0 ? `(${subsystems[subsystem.name_id].reaction_count})` : '' }}
                          </li>
                          <li v-else class="clickable disable">
                             {{ subsystem.name }}
                          </li>
                        </template>
                        <template v-else-if="subsystemsSVG">
                          <li v-for="subsystem in subsystems[system]" class="clickable" :class="{ 'disable' : !subsystemsSVG[subsystem.name_id].sha }"
                            v-if="system !== 'Collection of reactions' && subsystemsSVG[subsystem.name_id]" @click="showSubsystem(subsystem.name_id)">
                              {{ subsystem.name }} {{ subsystemsSVG[subsystem.name_id].reaction_count != 0 ? `(${subsystemsSVG[subsystem.name_id].reaction_count})` : '' }}
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
                  <ul class="vhs l1" v-if="subsystems['']">
                    <template v-if="!has2DSubsystemMaps || show3D">
                      <li v-for="subsystem in subsystems['']" class="clickable"
                        @click="showSubsystem(subsystem.name_id)">
                          {{ subsystem.name }} {{ subsystemsStats[subsystem.name_id].reaction_count != 0 ? `(${subsystemsStats[subsystem.name_id].reaction_count})` : '' }}
                      </li>
                    </template>
                    <template v-else-if="subsystemsSVG">
                      <li v-for="subsystem in subsystems['']" class="clickable" :class="{ 'disable' : !subsystemsSVG[subsystem.name_id].sha }"
                        v-if="subsystemsSVG[subsystem.name_id]" @click="showSubsystem(subsystem.name_id)">
                          {{ subsystem.name }} {{ subsystemsSVG[subsystem.name_id].reaction_count != 0 ? `(${subsystemsSVG[subsystem.name_id].reaction_count})` : '' }}
                      </li>
                      <li v-else class="clickable disable">
                         {{ subsystem.name }}
                      </li>
                    </template>
                  </ul>
                </template>
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
                        <template v-if="show3D">
                          {{ capitalize(currentDisplayedType) }}: {{ compartments[currentDisplayedName].name }}
                        </template>
                        <template v-else>
                          {{ capitalize(currentDisplayedType) }}: {{ compartmentsSVG[currentDisplayedName].name }}
                        </template>
                      </template>
                      <template v-else-if="currentDisplayedType === 'subsystem'">
                        <template v-if="show3D">
                          {{ capitalize(currentDisplayedType) }}: {{ subsystemsStats[currentDisplayedName].name }}
                        </template>
                        <template v-else>
                          {{ capitalize(currentDisplayedType) }}: {{ subsystemsSVG[currentDisplayedName].name }}
                        </template>
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
                          <template v-if="selectedElementHasNoData()">
                            {{ $t('noInfoAvailable') }}
                          </template>
                        </template>
                        <template v-else>
                          <template v-if="show3D">
                            <span class="hd"># reactions:</span> {{ subsystemsStats[idfy(selectedElementData.id)]['reaction_count'] }}<br>
                            <span class="hd"># metabolites:</span> {{ subsystemsStats[idfy(selectedElementData.id)]['metabolite_count'] }}<br>
                            <span class="hd"># enzymes:</span> {{ subsystemsStats[idfy(selectedElementData.id)]['enzyme_count'] }}<br>
                            <span class="hd"># compartments:</span> {{ subsystemsStats[idfy(selectedElementData.id)]['compartment_count'] }}<br>
                          </template>
                          <template v-else>
                            <!-- show the stats of the model not the maps -->
                            <span class="hd">Total model stats:</span><br>
                            <span class="hd"># reactions:</span> {{ subsystemsStats[subsystemsSVG[idfy(selectedElementData.id)].subsystem]['reaction_count'] }}<br>
                            <span class="hd"># metabolites:</span> {{ subsystemsStats[subsystemsSVG[idfy(selectedElementData.id)].subsystem]['metabolite_count'] }}<br>
                            <span class="hd"># enzymes:</span> {{ subsystemsStats[subsystemsSVG[idfy(selectedElementData.id)].subsystem]['enzyme_count'] }}<br>
                            <span class="hd"># compartments:</span> {{ subsystemsStats[subsystemsSVG[idfy(selectedElementData.id)].subsystem]['compartment_count'] }}<br>
                          </template>
                        </template>
                      </template>
                      <template v-else>
                        <template v-if="currentDisplayedType === 'compartment'">
                          <template v-if="show3D">
                            <span class="hd"># reactions:</span> {{ compartments[currentDisplayedName]['reaction_count'] }}<br>
                            <span class="hd"># metabolites:</span> {{ compartments[currentDisplayedName]['metabolite_count'] }}<br>
                            <span class="hd"># enzymes:</span> {{ compartments[currentDisplayedName]['enzyme_count'] }}<br>
                            <span class="hd"># subsystems:</span> {{ compartments[currentDisplayedName]['subsystem_count'] }}<br>
                          </template>
                          <template v-else>
                            <!-- show the stats of the model not the maps -->
                            <span class="hd"># reactions:</span> {{ compartments[compartmentsSVG[currentDisplayedName].compartment]['reaction_count'] }}<br>
                            <span class="hd"># metabolites:</span> {{ compartments[compartmentsSVG[currentDisplayedName].compartment]['metabolite_count'] }}<br>
                            <span class="hd"># enzymes:</span> {{ compartments[compartmentsSVG[currentDisplayedName].compartment]['enzyme_count'] }}<br>
                            <span class="hd"># subsystems:</span> {{ compartments[compartmentsSVG[currentDisplayedName].compartment]['subsystem_count'] }}<br>
                          </template>
                        </template>
                        <template v-else>
                          <template v-if="show3D">
                            <span class="hd"># reactions:</span> {{ subsystemsStats[currentDisplayedName]['reaction_count'] }}<br>
                            <span class="hd"># metabolites:</span> {{ subsystemsStats[currentDisplayedName]['metabolite_count'] }}<br>
                            <span class="hd"># enzymes:</span> {{ subsystemsStats[currentDisplayedName]['enzyme_count'] }}<br>
                            <span class="hd"># compartments:</span> {{ subsystemsStats[currentDisplayedName]['compartment_count'] }}<br>
                          </template>
                          <template v-else>
                            <!-- show the stats of the model not the maps -->
                            <span class="hd"># reactions:</span> {{ subsystemsStats[subsystemsSVG[currentDisplayedName].subsystem]['reaction_count'] }}<br>
                            <span class="hd"># metabolites:</span> {{ subsystemsStats[subsystemsSVG[currentDisplayedName].subsystem]['metabolite_count'] }}<br>
                            <span class="hd"># enzymes:</span> {{ subsystemsStats[subsystemsSVG[currentDisplayedName].subsystem]['enzyme_count'] }}<br>
                            <span class="hd"># compartments:</span> {{ subsystemsStats[subsystemsSVG[currentDisplayedName].subsystem]['compartment_count'] }}<br>
                          </template>
                        </template>
                      </template>
                    </div>
                  </div>
                  <footer class="card-footer"
                    v-if="['metabolite', 'enzyme', 'reaction', 'subsystem'].includes(selectedElement) || currentDisplayedType === 'subsystem'">
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
import Svgmap from 'components/explorer/mapViewer/Svgmap';
import D3dforce from 'components/explorer/mapViewer/D3dforce';
import Logo from '../../assets/logo.svg';
import { default as EventBus } from '../../event-bus';
import { capitalize, reformatStringToLink, idfy } from '../../helpers/utils';
import { chemicalReaction } from '../../helpers/chemical-formatters';
import { getExpLvlLegend } from '../../expression-sources/hpa';

export default {
  name: 'map-viewer',
  components: {
    Svgmap,
    D3dforce,
  },
  data() {
    return {
      Logo,
      model: '',
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
      initialEmit: false,
      showLoader: false,

      compartments: {},
      compartmentsSVG: {},
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
          'lipid particle',
          'mitochondrion',
          'mitochondrial_membrane',
          'nucleus',
          'peroxisome',
          'vacuole',
          'vacuolar_membrane',
        ],
      },
      subsystems: {},
      subsystemsStats: {},
      subsystemsSVG: {},
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
        yeast: {
          metabolite: [],
          enzyme: [],
          reaction: [],
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
  // watch: {
  //   /* eslint-disable quote-props */
  //   '$route': function watchSetup() {
  //     this.setup();
  //   },
  // },
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
        this.handleLoadComplete(false, this.$t('mapNotFound'));
        return;
      }
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
        this.loadErrorMesssage = errorMessage;
        if (!this.loadErrorMesssage) {
          this.loadErrorMesssage = this.$t('unknownError');
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
      const model = this.$route.params.model || '';
      if (!(model in this.selectedElementDataKeys)) {
        // TODO use another way to check the model id is valid
        this.model = '';
        EventBus.$emit('modelSelected', '');
        this.errorMessage = `Error: ${this.$t('modelNotFound')}`;
        return;
      }
      if (model !== this.model) {
        this.loadSubComptData(model);
        this.loadHPATissue(model);
      }
      this.model = model;
    },
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
    selectedElementHasNoData() {
      if (!(this.selectedElementData.type in this.selectedElementDataKeys)) {
        return true;
      }
      for (const k of this.selectedElementDataKeys[this.selectedElementData.type]) {
        if (k in this.selectedElementData &&
          this.selectedElementData[this.selectedElementData.type][k]) {
          return false;
        }
      }
      return true;
    },
    viewOnGemBrowser() {
      if (this.currentDisplayedType === 'subsystem') {
        EventBus.$emit('navigateTo', 'GEMBrowser', this.model, this.currentDisplayedType, this.currentDisplayedName);
      } else {
        EventBus.$emit('navigateTo', 'GEMBrowser', this.model, this.selectedElementData.type, this.selectedElementData.id);
      }
    },
    // globalMapSelected() {
    //   this.accordionLevelSelected = 'wholemap';
    //   this.switch3Dimension(false);
    //   EventBus.$emit('showSVGmap', 'wholemap', null, []);
    // },
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
      // console.log(`${isSuccess} ${errorMessage}`);
      if (!isSuccess) {
        // show error
        this.loadErrorMesssage = errorMessage;
        if (!this.loadErrorMesssage) {
          this.loadErrorMesssage = this.$t('unknownError');
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
      this.$router.push({ path: `/explore/map-viewer/${this.model}/${this.currentDisplayedType}/${this.currentDisplayedName}?dim=${this.show2D ? '2d' : '3d'}` });
      this.showLoader = false;
    },
    loadSubComptData(model) {
      axios.get(`${model}/viewer/`)
      .then((response) => {
        this.compartments = {};
        for (const c of response.data.compartment) {
          this.compartments[c.name_id] = c;
        }
        this.compartmentsSVG = {};
        for (const c of response.data.compartmentsvg) {
          this.compartmentsSVG[c.name_id] = c;
        }
        this.has2DCompartmentMaps = Object.keys(this.compartmentsSVG).length !== 0;
        this.subsystemsStats = {};
        for (const s of response.data.subsystem) {
          this.subsystemsStats[s.name_id] = s;
        }
        this.subsystemsSVG = {};
        for (const s of response.data.subsystemsvg) {
          this.subsystemsSVG[s.name_id] = s;
          // if (s.subsystem) {
          //   this.subsystemsStats[s.subsystem].id = s.id;
          // } else {
          //   this.subsystemsStats[s.id].id = s.id;
          // }
        }
        this.has2DSubsystemMaps = Object.keys(this.subsystemsSVG).length !== 0;
        const systems = response.data.subsystem.reduce((subarray, el) => {
          const arr = subarray;
          if (!arr[el.system]) { arr[el.system] = []; }
          el.id = this.subsystemsStats[el.name_id].id; // eslint-disable-line no-param-reassign
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

        if (!this.has2DCompartmentMaps && !this.has2DSubsystemMaps) {
          this.disabled2D = true;
          this.show3D = true;
          this.show2D = false;
        }

        // load maps from url if contains map_id, the url is then cleaned of the id
        if (this.$route.name === 'viewerCompartment' || this.$route.name === 'viewerSubsystem') {
          const type = this.$route.name === 'viewerCompartment' ? 'compartment' : 'subsystem';
          const mapID = this.$route.params.id;
          if (!this.$route.query.dim) {
            this.show2D = false;
          } else {
            this.show2D = this.$route.query.dim === '2d' && !this.disabled2D;
          }
          this.show3D = !this.show2D;
          this.$nextTick(() => {
            EventBus.$emit('showAction', type, mapID, [], false);
          });
        }
      })
      .catch((error) => {
        // console.log(error);
        switch (error.response.status) {
          default:
            this.errorMessage = this.$t('unknownError');
        }
      });
    },
    loadHPATissue(model) {
      axios.get(`${model}/enzyme/hpa_tissue/`)
        .then((response) => {
          this.HPATissue = response.data;
        })
        .catch((error) => {
          switch (error.response.status) {
            default:
              this.loadErrorMesssage = this.$t('unknownError');
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
          return this.requestedName in this.compartmentsSVG;
        }
        return this.requestedName in this.subsystemsSVG;
      }
      if (displayType === 'compartment') {
        return this.requestedName in this.compartments;
      }
      return this.requestedName in this.subsystemsStats;
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
    idfy,
  },
};
</script>

<style lang="scss">

$navbar-height: 2.5rem;
$footer-height: 5.1rem;

#mapViewer {
  /* border: 1px solid black; */
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
    /* border: 1px solid darkgray; */
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
          cursor: not-allowed;
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
