<template>
  <div class="closest-interaction-partners">
    <loader v-show="loading"></loader>
    <div v-show="!loading">
      <div v-if="errorMessage" class="columns">
        <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
          {{ errorMessage }}
        </div>
      </div>
      <div v-show="!errorMessage">
        <div class="container columns">
          <div class="column is-5">
            <h3 class="title is-3 is-marginless" v-html="title"></h3>
          </div>
          <div class="column is-3">
            <nav class="breadcrumb is-small is-pulled-right" aria-label="breadcrumbs" v-show="showNetworkGraph">
              <ul>
                <li :class="{'is-active' : false }">
                  <a @click="scrollTo('cip-graph')">Cytoscape graph</a>
                  </li>
                <li :class="{'is-active' : false }">
                  <a @click="scrollTo('cip-table')">Metabolite list</a>
                  </li>
              </ul>
            </nav>
          </div>
          <div class="column">
            <div class="dropdown" id="dropdownMenuExport">
              <div class="dropdown-trigger">
                <button class="button is-primary" aria-haspopup="true" aria-controls="dropdown-menu"
                @click="showMenuExport=!showMenuExport" v-show="showNetworkGraph">
                  <span>Export graph</span>
                  <span class="icon is-small">
                    &#9663;
                  </span>
                </button>
              </div>
              <div class="dropdown-menu" id="dropdown-menu" role="menu" v-show="showMenuExport"
              v-on:mouseleave="showMenuExport = false">
                <div class="dropdown-content">
                  <a class="dropdown-item" v-on:click="exportGraphml">
                    Graphml
                  </a>
                  <a class="dropdown-item" v-on:click="exportPNG">
                    PNG
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-show="showGraphContextMenu && showNetworkGraph" id="contextMenuGraph" ref="contextMenuGraph">
          <span v-show="clickedElmId !== id"
          class="button is-dark" v-on:click="navigate">Load interaction partners</span>
          <span v-show="!expandedIds.includes(clickedElmId)"
          class="button is-dark" v-on:click="loadExpansion">Expand interaction partners</span>
          <div v-show="clickedElm">
            <span class="button is-dark">Highlight reaction:</span>
          </div>
          <div>
            <template v-if="clickedElm !== null && clickedElm['reaction']">
               <template v-for="r, index of Array.from(clickedElm.reaction).slice(0,16)">
                <span class="button is-dark is-small has-margin-left" v-on:click="highlightReaction(r)" v-if="index != 15">
                  {{ r }}
                </span>
                <span v-else class="has-margin-left">
                  {{ `${Array.from(clickedElm.reaction).length - 15} others reaction(s)...` }}
                </span>
               </template>
            </template>
          </div>
          <div v-show="clickedElm && clickedElm.type === 'enzyme'">
            <!-- <span class="is-black sep is-paddingless"></span> -->
            <!-- <span class="button is-dark" v-on:click="viewReactionComponent('enzyme')">Show enzyme</span> -->
            <!-- <span class="is-black sep is-paddingless"></span> -->
<!--             <span class="button is-dark" v-on:click='visitLink(clickedElm.hpaLink, true)'>View in HPA &#8599;</span>
            <span v-show="clickedElm && clickedElm.type === 'enzyme' && clickedElm.details" class="button is-dark"
            v-on:click='visitLink(clickedElm.details.uniprot_link, true)'>View in Uniprot &#8599;</span> -->
          </div>
          <div v-show="clickedElm && clickedElm.type === 'metabolite'">
            <!-- <span class="is-black sep is-paddingless"></span> -->
            <!-- <span class="button is-dark" v-on:click="viewReactionComponent('metabolite')">Show metabolite</span> -->
            <!-- <span class="is-black sep is-paddingless"></span> -->
<!--             <span v-show="clickedElm && clickedElm.type === 'metabolite' && clickedElm.details" class="button is-dark"
            v-on:click='visitLink(clickedElm.details.hmdb_link, true)'>View in HMDB &#8599;</span>
            <span v-show="clickedElm && clickedElm.type === 'metabolite' && clickedElm.details" class="button is-dark"
            v-on:click='visitLink(clickedElm.details.pubchem_link, true)'>View in PUBCHEM &#8599;</span> -->
          </div>
        </div>
        <div id="cip-graph">
          <div v-show="showNetworkGraph" class="container columns">
            <div class="column is-8">
              <transition name="slide-fade">
                <article id="errorExpBar" class="message is-danger" v-if="errorExpMessage">
                  <div class="message-header">
                    <i class="fa fa-warning"></i>
                  </div>
                  <div class="message-body">
                    <h5 class="title is-5">{{ errorExpMessage }}</h5>
                  </div>
                </article>
              </transition>
              <div id="graphOption">
                <span class="button" v-bind:class="[{ 'is-active': showGraphLegend }, '']"
                v-on:click="toggleGraphLegend"><i class="fa fa-cog"></i></span>
                <span class="button" v-on:click="zoomGraph(true)"><i class="fa fa-search-plus"></i></span>
                <span class="button" v-on:click="zoomGraph(false)"><i class="fa fa-search-minus"></i></span>
                <span class="button" v-on:click="fitGraph()"><i class="fa fa-arrows-alt"></i></span>
                <span class="button" v-on:click="resetGraph(true)"><i class="fa fa-refresh"></i></span>
                <span class="button" v-on:click="resetGraph(false)" :disabled="reactionHL === null" :class="{'is-disabled': reactionHL === null }"><i class="fa fa-eraser"></i></span>
                <span class="button" v-on:click="viewReaction(reactionHL)" v-show="reactionHL">
                  {{ reactionHL }}
                </span>
              </div>
              <div v-show="showGraphLegend" id="contextGraphLegend" ref="contextGraphLegend">
                <button class="delete" v-on:click="toggleGraphLegend"></button>
                <span class="label">Enzyme</span>
                <div class="comp">
                  <span>Shape:</span>
                  <div class="select">
                    <select v-model="nodeDisplayParams.enzymeNodeShape" 
                    v-on:change="redrawGraph()">
                      <option v-for="shape in availableNodeShape">
                      {{ shape }}
                      </option>
                    </select>
                  </div>
                  <span>Color:</span>
                  <span class="color-span"
                    v-bind:style="{ background: nodeDisplayParams.enzymeNodeColor.hex }"
                    v-on:click="showColorPickerEnz = !showColorPickerEnz">
                    <compact-picker v-show="showColorPickerEnz"
                    v-model="nodeDisplayParams.enzymeNodeColor" @input="updateExpAndredrawGraph(false, 'enzyme')"></compact-picker>
                  </span>
                </div>
                <span class="label">Metabolite</span>
                <div class="comp">
                  <span>Shape:</span>
                  <div class="select">
                    <select v-model="nodeDisplayParams.metaboliteNodeShape" 
                    v-on:change="redrawGraph()">
                      <option v-for="shape in availableNodeShape">
                      {{ shape }}
                      </option>
                    </select>
                  </div>
                  <span>Color:</span>
                   <span class="color-span"
                    v-bind:style="{ background: nodeDisplayParams.metaboliteNodeColor.hex }"
                    v-on:click="showColorPickerMeta = !showColorPickerMeta">
                    <compact-picker v-show="showColorPickerMeta"
                    v-model="nodeDisplayParams.metaboliteNodeColor" @input="updateExpAndredrawGraph(false, 'metabolite')"></compact-picker>
                  </span>
                </div>
              </div>
              <div id="cy" ref="cy" class="card is-paddingless">
              </div>
            </div>
            <div class="column">
              <div class="columns" v-if="model === 'hmr2'">
                <div class="column">
                  <div class="card">
                    <header class="card-header">
                      <p class="card-header-title">
                        <label class="checkbox is-unselectable">
                          <input type="checkbox" v-model="toggleEnzymeExpLevel" :disabled="disableExpLvl"
                          @click="applyLevels('enzyme', 'HPA', 'RNA', selectedSample)">
                          Enable <a href="https://www.proteinatlas.org/" target="_blank">proteinAtlas.org</a>&nbsp;RNA levels
                        </label>
                      </p>
                    </header>
                    <div class="card-content" v-show="toggleEnzymeExpLevel">
                      <div id="graphLegend" v-show="(toggleMetaboliteExpLevel || toggleEnzymeExpLevel) && !disableExpLvl" v-html="legend">
                      </div>
                      <br>
                      <div class="select is-fullwidth" :class="{ 'is-loading' : loadingHPA && toggleEnzymeExpLevel}" v-show="toggleEnzymeExpLevel && !disableExpLvl">
                        <select id="enz-select" ref="enzHPAselect" v-model="selectedSample" :disabled="!toggleEnzymeExpLevel" 
                        @change.prevent="applyLevels('enzyme', 'HPA', 'RNA', selectedSample)">
                          <optgroup label="HPA - RNA levels - Tissues">
                           <!--  <option value="None">None</option> -->
                            <option v-for="tissue in tissues['HPA']" :value="tissue">
                              {{ tissue }}
                            </option>
                          </optgroup>
                          <optgroup label="HPA - RNA levels - Cell-type" v-if="false">
                            <option v-for="cellType in cellLines['HPA']" :value="cellType">
                              {{ cellType }}
                            </option>
                          </optgroup>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="columns" v-if="compartmentList.length != 0 || subsystemList.length != 0">
                <div class="column">
                  <div class="card">
                    <header class="card-header">
                      <p class="card-header-title">
                        Highlight&nbsp;
                        <span class="button has-margin-left" v-on:click="resetHighlight(false)" 
                        :disabled="isCompartmentSubsystemHLDisabled()"
                        :class="{'is-disabled': isCompartmentSubsystemHLDisabled() }">
                          <i class="fa fa-eraser"></i>
                        </span>
                      </p>
                    </header>
                     <div class="card-content">
                        <div class="select is-fullwidth">
                          <select v-model="compartmentHL" @change.prevent="highlightCompartment" :disabled="disableCompartmentHL">
                            <option value="" disabled v-if="!disableCompartmentHL">Select a compartment</option>
                            <option v-for="compartment in compartmentList" :value="disableCompartmentHL ? '' : compartment">
                              {{ compartment }}
                            </option>
                          </select>
                        </div>
                        <div v-show="subsystemList.length != 0">
                          <br>
                          <div class="select is-fullwidth">
                            <select v-model="subsystemHL" @change.prevent="highlightSubsystem">
                              <option value="" disabled>Select a subsystem</option>
                              <option v-for="sub in subsystemList" :value="sub">
                                {{ sub }}
                              </option>
                            </select>
                          </div>
                        </div>
                     </div>
                  </div>
                </div>
              </div>
              <div class="columns">
                <sidebar id="sidebar" :selectedElm="clickedElm" :view="'interaction'"" :model="model"></sidebar>
              </div>
            </div>
          </div>
          <div v-show="!showNetworkGraph" class="container columns">
            <div class="column is-4 is-offset-4 notification is-warning has-text-centered">
              <div v-html="$t('tooManyInteractionPartnerWarn')"></div>
              <span v-show="nodeCount <= maxNodeCount"
              class="button" v-on:click="generateGraph(fitGraph)">{{ $t('tooManyInteractionPartnerBut') }}</span>
            </div>
            <br>
          </div>
        </div>
        <div id="cip-table">
          <cytoscape-table
            :structure="tableStructure[model]"
            :elms="elms"
            :selected-elm-id="clickedElmId"
            :filename="filename"
            :sheetname="componentName"
            @highlight="highlightNode($event)"
          ></cytoscape-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue';
import axios from 'axios';
import cytoscape from 'cytoscape';
import jquery from 'jquery';
import graphml from 'cytoscape-graphml/src/index';
import cola from 'cytoscape-cola';
import { Compact } from 'vue-color';
import { default as FileSaver } from 'file-saver';

import Sidebar from 'components/explorer/gemBrowser/Sidebar';
import CytoscapeTable from 'components/explorer/gemBrowser/CytoscapeTable';
import Loader from 'components/Loader';

import { default as EventBus } from '../../../event-bus';

import { default as transform } from '../../../data-mappers/hmr-closest-interaction-partners';
import { default as graph } from '../../../graph-stylers/hmr-closest-interaction-partners';

import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../../../helpers/chemical-formatters';
import { default as visitLink } from '../../../helpers/visit-link';
import { default as convertGraphML } from '../../../helpers/graph-ml-converter';

import { getExpLvlLegend, getExpressionColor } from '../../../expression-sources/hpa';

export default {
  name: 'closest-interaction-partners',
  components: {
    Sidebar,
    CytoscapeTable,
    Loader,
    'compact-picker': Compact,
  },
  props: ['model'],
  data() {
    return {
      loading: true,
      loadingHPA: false,
      errorMessage: '',
      errorExpMessage: '',
      title: '',

      nodeCount: 0,
      warnNodeCount: 50,
      maxNodeCount: 100,
      showNetworkGraph: false,

      rawRels: {},
      rawElms: {},

      id: '',
      selectedElmId: '',
      selectedElm: null,

      clickedElmId: '',
      clickedElm: null,
      selectedSample: '',

      componentName: '',
      expandedIds: [],

      tissues: {},
      cellLines: {},
      legend: '',

      expSource: '',
      expType: '',
      expSample: '',

      reactionHL: null,
      compartmentHL: '',
      compartmentList: [],
      disableCompartmentHL: false,
      subsystemHL: '',
      subsystemList: [],

      // keep track of exp lvl source already loaded
      expSourceLoaded: {
        enzyme: {},
        metabolite: {},
      },
      disableExpLvl: false,

      cy: null,
      tableStructure: {
        hmr2: [
          { field: 'type', colName: 'Type' },
          { field: 'name', colName: 'Name' },
          { field: 'formula', colName: 'Formula', modifier: chemicalFormula },
          { field: 'compartment', colName: 'Compartment' },
        ],
      },

      showMenuExport: false,
      showMenuExpression: false,
      toggleEnzymeExpLevel: false,
      toggleMetaboliteExpLevel: false,

      showGraphLegend: false,
      showGraphContextMenu: false,
      showColorPickerEnz: false,
      showColorPickerMeta: false,

      availableNodeShape: [
        'rectangle',
        'roundrectangle',
        'cutrectangle',
        'ellipse',
        'rectangle',
        'triangle',
        'pentagon',
        'hexagon',
        'heptagon',
        'octagon',
        'star',
        'diamond',
        'vee',
        'rhomboid',
      ],

      nodeDisplayParams: {
        enzymeExpSource: false,
        enzymeExpType: false,
        enzymeExpSample: false,
        enzymeNodeShape: 'rectangle',
        enzymeNodeColor: {
          hex: '#C92F63',
          hsl: {
            h: 150, s: 0.5, l: 0.2, a: 1,
          },
          hsv: {
            h: 150, s: 0.66, v: 0.30, a: 1,
          },
          rgba: {
            r: 25, g: 77, b: 51, a: 1,
          },
          a: 1,
        },
        metaboliteExpSource: false,
        metaboliteExpType: false,
        metaboliteExpSample: false,
        metaboliteNodeShape: 'ellipse',
        metaboliteNodeColor: {
          hex: '#259F64',
          hsl: {
            h: 150, s: 0.5, l: 0.2, a: 1,
          },
          hsv: {
            h: 150, s: 0.66, v: 0.30, a: 1,
          },
          rgba: {
            r: 25, g: 77, b: 51, a: 1,
          },
          a: 1,
        },
      },
      maxZoom: 10,
      minZoom: 0.1,
      factorZoom: 0.08,
    };
  },
  computed: {
    filename() {
      return `ma_interaction_partners_${this.componentName}`;
    },
    elms() {
      if (Object.keys(this.rawElms).length !== 0) {
        return Object.keys(this.rawElms).map(k => this.rawElms[k]);
      }
      return [];
    },
    rels() {
      return Object.keys(this.rawRels).map(k => this.rawRels[k]);
    },
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.$route.path.includes('/interaction/')) {
        if (this.id !== this.$route.params.id) {
          this.setup();
        }
      }
    },
  },
  created() {
    graphml(cytoscape, jquery);
  },
  beforeMount() {
    cytoscape.use(cola);
    this.setup();
  },
  methods: {
    setup() {
      this.id = this.$route.params.id;
      this.selectedElmId = '';
      this.selectedElm = null;
      this.loadHPATissue();
      this.load();
    },
    navigate() {
      this.reactionHL = null;
      this.compartmentHL = '';
      this.subsystemHL = '';
      this.$router.push(`/explore/gem-browser/${this.model}/interaction/${this.clickedElmId}`);
    },
    loadHPATissue() {
      axios.get(`${this.model}/enzymes/hpa_tissue/`)
        .then((response) => {
          // this.tissues.HPA = response.data;
          Vue.set(this.tissues, 'HPA', response.data);
        })
        .catch((error) => {
          switch (error.response.status) {
            default:
              this.errorMessage = this.$t('unknownError');
          }
        });
    },
    load() {
      axios.get(`${this.model}/reaction_components/${this.id}/with_interaction_partners`)
        .then((response) => {
          this.loading = false;
          this.showGraphContextMenu = false;
          const component = response.data.component;
          const reactions = response.data.reactions;

          this.componentName = component.name || component.gene_name || component.id;
          this.id = component.id;
          if ('gene_name' in component) {
            // this.title = `${this.chemicalName(this.componentName)}`;
            this.title = this.componentName;
            if (component.uniprot != null) {
              this.title = `${this.title} (<a href="${component.uniprot_link}" target="_blank">${component.uniprot}</a>)`;
            }
            component.type = 'enzyme';
          } else {
            this.title = `${this.chemicalName(this.componentName)}`;
            component.type = 'metabolite';
          }

          [this.rawElms, this.rawRels, this.compartmentList, this.subsystemList] =
            transform(component, reactions, null, null, null, null);
          if (this.compartmentList.length === 1) {
            this.compartmentHL = '';
            this.disableCompartmentHL = true;
          }
          this.selectedElm = this.rawElms[component.id];
          this.selectedElm.name = this.componentName;

          this.expandedIds = [];
          this.expandedIds.push(component.id);

          this.nodeCount = Object.keys(this.rawElms).length;
          if (this.nodeCount > this.warnNodeCount) {
            this.showNetworkGraph = false;
            this.errorMessage = '';
            return;
          }
          this.showNetworkGraph = true;
          this.errorMessage = '';

          this.resetEnzymeExpression();

          // The set time out wrapper enforces this happens last.
          setTimeout(() => {
            this.constructGraph(this.rawElms, this.rawRels);
          }, 0);
        })
        .catch((error) => {
          this.loading = false;
          // console.log(error);
          switch (error.response.status) {
            case 406:
              this.errorMessage = this.$t('tooManyInteractionPartner');
              break;
            case 404:
              this.errorMessage = this.$t('notFoundError');
              break;
            default:
              this.errorMessage = this.$t('unknownError');
          }
        });
    },
    loadExpansion() {
      axios.get(`${this.model}/reaction_components/${this.clickedElmId}/with_interaction_partners`)
        .then((response) => {
          this.reactionHL = null;
          this.loading = false;
          this.errorMessage = null;
          this.showGraphContextMenu = false;

          const component = response.data.component;
          const reactions = response.data.reactions;
          [this.rawElms, this.rawRels, this.compartmentList, this.subsystemList] =
            transform(component, reactions, this.rawElms, this.rawRels,
             this.compartmentList, this.subsystemList);
          if (this.compartmentList.length === 1) {
            this.compartmentHL = '';
            this.disableCompartmentHL = true;
          } else {
            this.disableCompartmentHL = false;
          }

          // Object.assign(this.rawElms, newElms);
          // Object.assign(this.rawRels, newRels);
          // this.rawElms = this.loadHPAData(this.rawElms);

          this.expandedIds.push(component.id);

          this.nodeCount = Object.keys(this.rawElms).length;
          if (this.nodeCount > this.warnNodeCount) {
            this.showNetworkGraph = false;
            this.errorMessage = '';
            return;
          }
          this.showNetworkGraph = true;
          this.errorMessage = '';

          this.resetEnzymeExpression();

          // The set time out wrapper enforces this happens last.
          setTimeout(() => {
            this.constructGraph(this.rawElms, this.rawRels);
          }, 0);
        })
        .catch((error) => {
          // console.log(error);
          this.loading = false;
          switch (error.response.status) {
            case 406:
              this.errorExpMessage = this.$t('tooManyInteractionPartner');
              setTimeout(() => {
                this.errorExpMessage = '';
              }, 3000);
              break;
            case 404:
              this.errorMessage = this.$t('notFoundError');
              break;
            default:
              this.errorMessage = this.$t('unknownError');
          }
        });
    },
    isCompartmentSubsystemHLDisabled() {
      return ((this.compartmentHL === '' && this.subsystemHL === '') ||
        (this.compartmentList.length < 2 && this.subsystemList.length === 0));
    },
    highlightReaction(rid) {
      if (rid) {
        this.reactionHL = rid;
        this.redrawGraph();
        this.showGraphContextMenu = false;
      }
    },
    highlightCompartment() {
      if (this.compartmentHL) {
        this.redrawGraph();
      }
    },
    highlightSubsystem() {
      if (this.subsystemHL) {
        this.redrawGraph();
      }
    },
    toggleGraphLegend() {
      this.showGraphLegend = !this.showGraphLegend;
      this.showColorPickerEnz = false;
      this.showColorPickerMeta = false;
    },
    fixEnzSelectOption() {
      const option = document.getElementById('enz-select')
      .getElementsByTagName('optgroup')[0].childNodes[0];
      option.selected = 'selected';
      this.nodeDisplayParams.enzymeExpSample = option.label;
    },
    updateExpAndredrawGraph(usingExpressionLevel, nodeType, expSource, expType, expSample) {
      setTimeout(() => {
        if ((expSource && expType) && !expSample) {
          // fix option selection! because of optgroup?
          if (this.toggleEnzymeExpLevel) {
            this.fixEnzSelectOption();
          }
        }
        if (!usingExpressionLevel) {
          if ((nodeType === 'enzyme' && this.toggleEnzymeExpLevel) ||
            (nodeType === 'metabolite' && this.toggleMetaboliteExpLevel)) {
            return;
          }
        }
        this.redrawGraph();
      }, 0);
    },
    resetHighlight() {
      if (this.isCompartmentSubsystemHLDisabled()) {
        return;
      }
      this.compartmentHL = '';
      this.subsystemHL = '';
      this.redrawGraph();
    },
    resetGraph(reload) {
      this.reactionHL = null;
      this.selectedElm = null;
      this.selectedElmId = '';
      this.clickedElm = null;
      this.clickedElmId = '';
      this.resetEnzymeExpression();
      if (reload) {
        this.load();
      } else {
        this.redrawGraph();
      }
    },
    redrawGraph() {
      const stylesheet = graph(this.id,
        this.rawElms, this.rawRels, this.nodeDisplayParams,
         this.reactionHL, this.compartmentHL, this.subsystemHL)[1];
      const cyzoom = this.cy.zoom();
      const cypan = this.cy.pan();
      this.cy.style(stylesheet);
      this.cy.viewport({
        zoom: cyzoom,
        pan: cypan,
      });
    },
    fitGraph() {
      setTimeout(() => {
        this.cy.fit(null, 10);
        this.minZoom = this.cy.zoom() / 2.0;
      }, 300);
    },
    highlightNode(elmId) {
      if (!this.showNetworkGraph) {
        return;
      }
      this.cy.nodes().deselect();
      const node = this.cy.getElementById(elmId);
      node.json({ selected: true });
      node.trigger('tap');
    },
    generateGraph(callback) {
      this.showNetworkGraph = true;
      this.errorMessage = null;

      this.resetEnzymeExpression();

      // The set time out wrapper enforces this happens last.
      setTimeout(() => {
        this.constructGraph(this.rawElms, this.rawRels, callback);
      }, 0);
    },
    // this.switchSVG(compartmentID,
    constructGraph: function constructGraph(elms, rels, callback) {
      const [elements, stylesheet] = graph(this.id,
        elms, rels, this.nodeDisplayParams, this.reactionHL, this.compartmentHL, this.subsystemHL);
      // const id = this.id;

      const colaOptions = {
        animate: true, // whether to show the layout as it's running
        refresh: 0.1, // number of ticks per frame; higher is faster but more jerky
        maxSimulationTime: 10000, // max length in ms to run the layout
        ungrabifyWhileSimulating: false, // so you can't drag nodes during layout
        fit: true, // on every layout reposition of nodes, fit the viewport
        padding: 30, // padding around the simulation
        boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
        nodeDimensionsIncludeLabels: undefined,
        // whether labels should be included in determining the space used
        // by a node (default true)

        // layout event callbacks
        ready() {}, // on layoutready
        stop() {}, // on layoutstop

        // positioning options
        randomize: false, // use random node positions at beginning of layout
        avoidOverlap: true, // if true, prevents overlap of node bounding boxe
        handleDisconnected: true, // if true, avoids disconnected components from overlappin
        nodeSpacing() { return 10; }, // extra spacing around node
        flow: undefined,
        // use DAG/tree flow layout if specified, e.g. { axis: 'y', minSeparation: 30 }
        alignment: undefined,
        // relative alignment constraints on nodes,
        // e.g. function( node ){ return { x: 0, y: 1 } }
        // different methods of specifying edge length
        // each can be a constant numerical value or a function
        // like `function( edge ){ return 2; }
        edgeLength: undefined, // sets edge length directly in simulation
        edgeSymDiffLength: undefined, // symmetric diff edge length in simulation
        edgeJaccardLength: undefined, // jaccard edge length in simulation

        // iterations of cola algorithm; uses default values on undefined
        unconstrIter: undefined, // unconstrained initial layout iterations
        userConstIter: undefined, // initial layout iterations with user-specified constraints
        allConstIter: undefined,
        // initial layout iterations with all constraints including non-overlap

        // infinite layout options
        infinite: false, // overrides all other options for a forces-all-the-time mode
      };
      const id = this.id;
      this.cy = cytoscape({
        container: this.$refs.cy,
        elements,
        style: stylesheet,
        layout: {
          // check 'cola' layout extension
          name: Object.keys(elms).length > 30 ? 'concentric' : 'cola',
          colaOptions,
          concentric(node) {
            if (node.degree() === 1) {
              return 1;
            }
            if (node.data().id === id) {
              return 10000;
            }
            if (node.data().type === 'enzyme') {
              return 100;
            }
            return 200;
          },
          ready: this.fitGraph,
        },
      });
      this.cy.userZoomingEnabled(false);

      window.pageYOffset = 0;
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;

      const cyt = this.cy;
      cyt.on('zoom', () => {
        const dim = Math.ceil(10 / cyt.zoom());
        const edgeWidth = 1 / cyt.zoom();

        cyt.$('edge').css({
          width: edgeWidth,
          'font-size': dim / 2,
        });

        cyt.$('node').css({
          width: dim,
          height: dim,
          'font-size': dim,
          'text-opacity': 1,
          'overlay-padding': edgeWidth * 2,
        });
      });

      const contextMenuGraph = this.$refs.contextMenuGraph;
      this.showGraphContextMenu = false;
      this.showNetworkGraph = true;

      const updatePosition = (node) => {
        contextMenuGraph.style.left = `${node.renderedPosition().x + 15}px`;
        contextMenuGraph.style.top = `${node.renderedPosition().y + 130}px`;
      };

      const nodeInViewport = (node) => {
        if (node.renderedPosition().x < 0 || node.renderedPosition().x > this.cy.width()
          || node.renderedPosition().y < 0 || node.renderedPosition().y > this.cy.height()) {
          return false;
        }
        return true;
      };

      this.cy.on('tap', () => {
        this.showGraphContextMenu = false;
        this.clickedElmId = '';
        this.clickedElm = null;
      });

      this.cy.on('tap', 'node', (evt) => {
        const node = evt.target;
        const elmId = node.data().id;

        this.clickedElmId = elmId;
        this.clickedElm = this.rawElms[elmId];
        this.showGraphContextMenu = true;
        updatePosition(node);
      });

      this.cy.on('drag', 'node', (evt) => {
        const node = evt.target;
        if (this.clickedElmId === node.data().id && nodeInViewport(node)) {
          updatePosition(node);
        }
      });

      this.cy.on('tapstart', () => {
        this.showGraphContextMenu = false;
      });

      this.cy.on('tapdragout, tapend', () => {
        if (this.clickedElmId !== '') {
          const node = this.cy.getElementById(this.clickedElmId);
          if (!nodeInViewport(node)) {
            return;
          }
          // this.showGraphContextMenu = true;
          updatePosition(node);
        }
      });
      if (callback) {
        callback();
      }
    },
    // TODO: refactor
    exportGraphml: function exportGraphml() {
      this.cy.graphml({
        node: {
          css: true,
          data: true,
          position: true,
          discludeds: [],
        },
        edges: {
          css: true,
          data: true,
          discludeds: [],
        },
        layoutby: 'concentric',
      });

      const output = this.cy.graphml();
      const converted = convertGraphML(output);

      const blob = new Blob([converted], { type: 'text/graphml' });
      const filename = `${this.id}_interaction_partners.graphml`;
      FileSaver.saveAs(blob, filename);
    },
    exportPNG: function exportPNG() {
      const a = document.createElement('a');
      const output = this.cy.png({
        bg: 'white',
      });

      a.href = output;
      a.download = `${this.id}_interaction_partners.png`;
      a.target = '_blank';
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },
    applyLevels(componentType, expSource, expType, expSample) {
      setTimeout(() => {  // wait this.toggleEnzymeExpLevel
        // console.log('Type Source, Type, Sample', componentType, expSource, expType, expSample);
        if (this.disableExpLvl) {
          return;
        }
        this.expSource = expSource;
        this.expType = expType;
        this.expSample = expSample;
        if (componentType === 'enzyme') {
          if (this.toggleEnzymeExpLevel) {
            if (this.nodeDisplayParams.enzymeExpSource !== expSource) {
              this.nodeDisplayParams.enzymeExpSource = expSource;
              this.nodeDisplayParams.enzymeExpType = expType;
              // check if this source for ths type of component have been already loaded
              if (!Object.keys(this.expSourceLoaded[componentType]).length === 0 ||
                !this.expSourceLoaded[componentType][expSource]) {
                // sources that load all exp type
                if (expSource === 'HPA') {
                  this.getHPAexpression(this.rawElms, expSample);
                } else {
                  // load expression data from another source here
                }
              } else {
                this.updateExpAndredrawGraph(true, componentType, expSource, expType, expSample);
              }
            } else if (this.nodeDisplayParams.enzymeExpType !== expType) {
              this.nodeDisplayParams.enzymeExpType = expType;
              if (!this.expSourceLoaded.componentType.expSource.expType) {
                // sources that load only one specific exp type
                this.updateExpAndredrawGraph(true, componentType, expSource, expType, expSample);
              }
            } else if (this.nodeDisplayParams.enzymeExpSample !== expSample) {
              this.updateExpAndredrawGraph(true, componentType, expSource, expType, expSample);
            }
            this.nodeDisplayParams.enzymeExpSample = expSample;
          } else {
            // disable expression lvl for enzyme
            this.nodeDisplayParams.enzymeExpSource = false;
            this.nodeDisplayParams.enzymeExpType = false;
            this.nodeDisplayParams.enzymeExpSample = false;
            this.updateExpAndredrawGraph(true, componentType, expSource, expType, expSample);
          }
        } else if (this.toggleMetaboliteExpLevel) {
          // load data for metabolite
        } else {
          // disable lvl for metabolite
          this.nodeDisplayParams.metaboliteExpSource = false;
          this.nodeDisplayParams.metaboliteExpType = false;
          this.nodeDisplayParams.metaboliteExpSample = false;
        }
      }, 0);
    },
    zoomGraph: function zoomGraph(zoomIn) {
      let factor = this.factorZoom;
      if (!zoomIn) {
        factor = -factor;
      }

      const zoom = this.cy.zoom();
      let lvl = zoom + (zoom * factor);

      if (lvl < this.minZoom) {
        lvl = this.minZoom;
      }

      if (lvl > this.maxZoom) {
        lvl = this.maxZoom;
      }

      if ((lvl === this.maxZoom && zoom === this.maxZoom) ||
        (lvl === this.minZoom && zoom === this.minZoom)) {
        return;
      }

      this.cy.zoom({
        level: lvl,
      });
    },
    viewReactionComponent(type) {
      EventBus.$emit('GBnavigateTo', type,
       this.selectedElm.real_id ? this.selectedElm.real_id : this.selectedElm.id);
    },
    viewReaction(ID) {
      EventBus.$emit('GBnavigateTo', 'reaction', ID);
    },
    scrollTo(id) {
      const container = jquery('body, html');
      container.scrollTop(
        jquery(`#${id}`).offset().top - (container.offset().top + container.scrollTop())
      );
    },
    resetEnzymeExpression() {
      this.toggleEnzymeExpLevel = false;
      this.nodeDisplayParams.enzymeExpSource = false;
      this.nodeDisplayParams.enzymeExpType = false;
      this.nodeDisplayParams.enzymeExpSample = false;
      this.expSourceLoaded.enzyme = {};
    },
    getHPAexpression(rawElms) {
      this.loadingHPA = true;
      const enzymes = Object.keys(rawElms).filter(el => rawElms[el].type === 'enzyme');
      const enzymeIDs = enzymes.map(k => rawElms[k].id);

      axios.post(`${this.model}/enzymes/hpa_rna_levels/`, { data: enzymeIDs })
      .then((response) => {
        const matLevels = response.data.levels;
        for (let i = 0; i < matLevels.length; i += 1) {
          const array = matLevels[i];
          const enzID = array[0];

          if (!(enzID in this.rawElms)) {
            continue; // eslint-disable-line no-continue
          }

          if (!this.rawElms[enzID].expressionLvl) {
            this.rawElms[enzID].expressionLvl = {};
          }
          if (!this.rawElms[enzID].expressionLvl.HPA) {
            this.rawElms[enzID].expressionLvl.HPA = {};
          }
          if (!this.rawElms[enzID].expressionLvl.HPA.RNA) {
            this.rawElms[enzID].expressionLvl.HPA.RNA = {};
          }

          const levels = array[1].split(',').map(v => Math.round((parseFloat(v + 1) + 0.00001) * 100) / 100);
          for (let j = 0; j < this.tissues.HPA.length; j += 1) {
            const tissue = this.tissues.HPA[j];
            this.rawElms[enzID].expressionLvl.HPA.RNA[tissue] = getExpressionColor(levels[j]);
          }
        }
        this.expSourceLoaded.enzyme.HPA = {};
        this.expSourceLoaded.enzyme.HPA.RNA = true;
        this.legend = getExpLvlLegend();
        this.disableExpLvl = false;
        this.loadingHPA = false;
        setTimeout(() => {
          // if ((expSource && expType) && !expSample) {
            // fix option selection! because of optgroup?
            // if (this.toggleEnzymeExpLevel) {
          this.fixEnzSelectOption();
            // }
          //  }
          this.redrawGraph(true);
        }, 0);
      })
      .catch(() => {
        this.loadingHPA = false;
        this.toggleEnzymeExpLevel = false;
        this.disableExpLvl = true;
        this.nodeDisplayParams.enzymeExpSource = false;
        this.nodeDisplayParams.enzymeExpType = false;
        this.nodeDisplayParams.enzymeExpSample = false;
      });
    },
    chemicalFormula,
    chemicalName,
    chemicalNameExternalLink,
    visitLink,
  },
};
</script>

<style lang='scss'>
.closest-interaction-partners {

  h1, h2 {
    font-weight: normal;
  }

  #cy {
    /* position: static; */
    margin: auto;
    height: 820px;
  }

  #sidebar {
    max-height: 820px;
    overflow-y: auto;
  }

  #dropdownMenuExport {
    .dropdown-menu {
      display: block;
    }
  }

  #contextMenuGraph, #contextMenuExport, #contextMenuExpression {
    position: absolute;
    z-index: 20;

    span {
      display: block;
      padding: 5px 10px;
      text-align: left;
      border-radius: 0;
      a {
        color: white;
      }
    }

    span.sep.is-black {
      background: #363636;
      border-bottom: 1px solid black;
      height: 1px;
    }
  }

  #errorExpBar {
    position: absolute;
    top: 12px;
    left: 12px;
    z-index: 11;
  }

  #graphOption {
    position: absolute;
    top: 12px;
    left: 12px;
    height: 30px;
    z-index: 10;

    span {
      display: inline-block;
      margin-right: 5px;
    }

    select {
      padding: 3px;
    }
  }

  #contextGraphLegend {
    position: absolute;
    background: white;
    top: 44px;
    left: 12px;
    width: auto;
    height: auto;
    padding: 15px;
    border: 1px solid black;
    border-radius: 2px;
    z-index: 30;

    span, div.select, compact-picker {
      display: inline-block;
      margin-right: 20px;
      margin-bottom: 10px;
    }

    div.comp {
      margin-left: 20px;
      display: block;
    }

    span.label {
      display: block;
      margin-left: 0;
    }

    .delete {
      position : absolute;
      right: 10px;
      top: 10px;
    }

    span.color-span {
      height: 20px;
      width: 25px;
      border: 1px solid black;
      vertical-align: middle;
      margin-right: 15px;
      margin-bottom: 5px;
    }

    span.color-span:hover {
      cursor: pointer;
    }
  }

  #t-select {
    margin-top: 0.75rem;
  }

  #enz-select {
    min-width: 240px;
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
