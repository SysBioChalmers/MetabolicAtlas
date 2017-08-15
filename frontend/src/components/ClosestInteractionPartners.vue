<template>
  <div class="closest-interaction-partners">
    <loader v-show="loading"></loader>
    <div v-show="!loading">
      <div v-show="errorMessage" class="notification is-danger">
        {{ errorMessage }}
      </div>
      <div v-show="!errorMessage">
        <div class="container columns">
          <div class="column is-8">
            <h3 class="title is-3 is-marginless" v-html="title"></h3>
          </div>
          <div class="column">
            <div class="dropdown" id="dropdownMenuExport">
              <div class="dropdown-trigger">
                <button class="button is-primary" aria-haspopup="true" aria-controls="dropdown-menu"
                @click="showMenuExport=!showMenuExport">
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
          <span v-show="selectedElmId !== reactionComponentId"
          class="button is-dark" v-on:click="navigate">Load interaction partners</span>
          <span v-show="!expandedIds.includes(selectedElmId)"
          class="button is-dark" v-on:click="loadExpansion">Expand interaction partners</span>
          <span class="button is-dark" v-on:click="highlightReaction">Highlight reaction</span>
          <div v-show="selectedElm && selectedElm.type === 'enzyme'">
            <span class="is-black sep is-paddingless"></span>
            <span class="button is-dark" v-on:click="viewReactionComponent(3)">Show enzyme</span>
            <span class="is-black sep is-paddingless"></span>
            <span class="button is-dark" v-on:click='visitLink(selectedElm.hpaLink, true)'>View in HPA &#8599;</span>
            <span v-show="selectedElm && selectedElm.type === 'enzyme' && selectedElm.details" class="button is-dark"
            v-on:click='visitLink(selectedElm.details.uniprot_link, true)'>View in Uniprot &#8599;</span>
          </div>
          <div v-show="selectedElm && selectedElm.type === 'metabolite'">
            <span class="is-black sep is-paddingless"></span>
            <span class="button is-dark" v-on:click="viewReactionComponent(4)">Show metabolite</span>
            <span class="is-black sep is-paddingless"></span>
            <span v-show="selectedElm && selectedElm.type === 'metabolite' && selectedElm.details" class="button is-dark"
            v-on:click='visitLink(selectedElm.details.hmdb_link, true)'>View in HMDB &#8599;</span>
            <span v-show="selectedElm && selectedElm.type === 'metabolite' && selectedElm.details" class="button is-dark"
            v-on:click='visitLink(selectedElm.details.pubchem_link, true)'>View in PUBCHEM &#8599;</span>
          </div>
        </div>
        <div v-show="showNetworkGraph" class="container columns">
          <div class="column is-8">
            <div id="graphOption">
              <span class="button" v-bind:class="[{ 'is-active': showGraphLegend }, '']"
              v-on:click="toggleGraphLegend">Options</span>
              <span class="button" v-on:click="zoomGraph(true)">+</span>
              <span class="button" v-on:click="zoomGraph(false)">-</span>
              <span class="button" v-on:click="fitGraph()">fit</span>
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
                  v-model="nodeDisplayParams.enzymeNodeColor" @input="redrawGraph(false, 'enzyme')"></compact-picker>
                </span>
              </div>
              <div class="comp">
                <label class="checkbox">
                  <input type="checkbox" v-model="toggleEnzymeExpLevel" @click="switchToExpressionLevel('enzyme', 'HPA', 'RNA', selectedSample)">
                  <span>Show expression levels</span>
                </label>
                <div class="comp">
                  <div class="select">
                    <select id="enz-select" ref="enzHPAselect" v-model="selectedSample" :disabled="!toggleEnzymeExpLevel" 
                    @change.prevent="switchToExpressionLevel('enzyme', 'HPA', 'RNA', selectedSample)">
                      <optgroup label="HPA - RNA levels - Tissues">
                        <option v-for="tissue in hpaTissues" :value="tissue">
                          {{ tissue }}
                        </option>
                      </optgroup>
                      <optgroup label="HPA - RNA levels - Cell-type" v-if="false">
                        <option v-for="cellType in hpaCellLines" :value="cellType">
                          {{ cellType }}
                        </option>
                      </optgroup>
                    </select>
                  </div>
                </div>
              </div>
              <hr>
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
                  v-bind:style="{ background: nodeDisplayParams.metaboliteNodeColor.hex}"
                  v-on:click="showColorPickerMeta = !showColorPickerMeta">
                  <compact-picker v-show="showColorPickerMeta"
                  v-model="nodeDisplayParams.metaboliteNodeColor" @input="redrawGraph(false, 'metabolite')"></compact-picker>
                </span>
              </div>
            </div>
            <div id="cy" ref="cy" class="card is-paddingless">
            </div>
          </div>
          <sidebar id="sidebar" :selectedElm="selectedElm"></sidebar>
        </div>
        <div v-show="!showNetworkGraph" class="container columns">
          <div class="column is-4 is-offset-4 notification is-warning has-text-centered">
            <div v-html="$t('tooManyReactionsWarn')"></div>
            <span v-show="reactionsCount <= maxReactionCount"
            class="button" v-on:click="constructGraph(rawElms, rawRels, fitGraph)">{{ $t('tooManyReactionsBut') }}</span>
          </div>
        </div>
        <cytoscape-table
          :structure="tableStructure"
          :elms="elms"
          :selected-elm-id="selectedElmId"
          :filename="filename"
          :sheetname="componentName"
          @highlight="highlightNode($event)"
        ></cytoscape-table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import cytoscape from 'cytoscape';
import jquery from 'jquery';
import graphml from 'cytoscape-graphml/src/index';
import viewUtilities from 'cytoscape-view-utilities';
import { Compact } from 'vue-color';
import { default as FileSaver } from 'file-saver';
import Sidebar from 'components/Sidebar';
import CytoscapeTable from 'components/CytoscapeTable';
import Loader from 'components/Loader';
import { default as EventBus } from '../event-bus';
import { default as transform } from '../data-mappers/closest-interaction-partners';
import { default as graph } from '../graph-stylers/closest-interaction-partners';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../helpers/chemical-formatters';
import { fetchXML, parseXML } from '../helpers/xml-tools';
import { default as visitLink } from '../helpers/visit-link';
import { default as convertGraphML } from '../helpers/graph-ml-converter';

export default {
  name: 'closest-interaction-partners',
  components: {
    Sidebar,
    CytoscapeTable,
    Loader,
    'compact-picker': Compact,
  },
  data() {
    return {
      loading: true,
      errorMessage: this.$t('unknownError'),
      title: '',

      reactionsCount: 0,
      warnReactionCount: 10,
      maxReactionCount: 100,
      showNetworkGraph: false,

      rawRels: {},
      rawElms: {},

      reactionComponentId: '',
      selectedElmId: '',

      selectedElm: null,
      selectedSample: '',

      componentName: '',
      expandedIds: [],

      hpaTissues: [],
      hpaCellLines: [],

      // keep track of exp lvl source already loaded
      expSourceLoaded: {
        enzyme: {},
        metabolite: {},
      },

      cy: null,
      tableStructure: [
        { field: 'type', colName: 'Type', modifier: false },
        { field: 'short', colName: 'Short name', modifier: false, rc: 'type' },
        { field: 'long', colName: 'Long name', modifier: chemicalName },
        { field: 'formula', colName: 'Formula', modifier: chemicalFormula },
        { field: 'compartment', colName: 'Compartment', modifier: false },
      ],

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
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  computed: {
    filename() {
      return `ma_interaction_partners_${this.componentName}`;
    },
    elms() {
      return Object.keys(this.rawElms).map(k => this.rawElms[k]);
    },
    rels() {
      return Object.keys(this.rawRels).map(k => this.rawRels[k]);
    },
  },
  beforeMount() {
    graphml(cytoscape, jquery);
    viewUtilities(cytoscape, jquery);
    this.setup();
  },
  methods: {
    setup() {
      this.reactionComponentId = this.$route.query.reaction_component_id
                                  || this.$route.query.reaction_component_long_name;
      this.selectedElmId = '';
      this.selectedElm = null;
      this.load();
    },
    navigate() {
      this.$router.push(
        { query: { ...this.$route.query, reaction_component_id: this.selectedElmId } },
        () => { // On complete.
          this.showMetaboliteTable = false;
          this.setup();
        },
        () => { // On abort.
          this.showGraphContextMenu = false;
          this.selectedElmId = '';
          this.selectedElm = null;
        }
      );
    },
    load() {
      axios.get(`reaction_components/${this.reactionComponentId}/with_interaction_partners`)
        .then((response) => {
          this.loading = false;
          const component = response.data.component;
          const reactions = response.data.reactions;

          this.componentName = component.short_name || component.long_name;
          this.reactionComponentId = component.id;
          if (component.enzyme) {
            const uniprotLink = component.enzyme ? component.enzyme.uniprot_link : null;
            const uniprotId = uniprotLink.split('/').pop();
            this.title = `Closest interaction partners | ${this.chemicalName(this.componentName)}
              (<a href="${uniprotLink}" target="_blank">${uniprotId}</a>)`;
          } else {
            this.title = `Closest interaction partners | ${this.chemicalName(this.componentName)}`;
          }

          [this.rawElms, this.rawRels] = transform(component, component.id, reactions);
          this.selectedElm = this.rawElms[component.id];
          // this.rawElms = this.loadHPAData(this.rawElms);
          this.selectedElm.name = this.componentName;

          this.expandedIds = [];
          this.expandedIds.push(component.id);

          this.reactionCount = response.data.reactions.length;
          if (this.reactionCount > this.warnReactionCount) {
            this.showNetworkGraph = false;
            this.errorMessage = '';
            return;
          }
          this.showNetworkGraph = true;
          this.errorMessage = null;

          // The set time out wrapper enforces this happens last.
          setTimeout(() => {
            this.constructGraph(this.rawElms, this.rawRels);
          }, 0);
        })
        .catch((error) => {
          this.loading = false;
          console.log(error);
          switch (error.response.status) {
            case 406:
              this.errorMessage = this.$t('tooManyInteractionPartners');
              break;
            default:
              this.errorMessage = this.$t('unknownError');
          }
        });
    },
    loadHPAData(rawElms) {
      // get the list of enzyme ids
      const enzymes = Object.keys(rawElms).filter(el => rawElms[el].type === 'enzyme');
      const enzymeIDs = enzymes.map(k => rawElms[k].long);

      const baseUrl = 'http://www.proteinatlas.org/search/external_id:';
      const proteins = `${enzymeIDs.join(',')}?format=xml`;
      const url = baseUrl + proteins;

      const xmlContent = fetchXML(url);
      if (xmlContent === '') {
        return [];
      }
      const xmlDoc = parseXML(xmlContent);
      const genes = xmlDoc.getElementsByTagName('entry');
      const hpaGeneEx = {};
      this.hpaTissues = {};
      this.hpaCellLines = {};
      for (const gene of genes) {
        console.log(`gene JSON.stringyfy(${gene})`);
        const genename = gene.getElementsByTagName('name')[0].textContent;
        hpaGeneEx[genename] = [];
        const samples = gene.getElementsByTagName('rnaExpression')[0].getElementsByTagName('data');
        // Loop through rnaExpression children 'samples'
        for (let i = 0; i < samples.length; i += 1) {
          let sampleType;
          let sampleName;
          let replicates = [];
          // Collect log2(tpm) expression values and sample name of one sample
          for (const sampleEl of samples[i].children) {
            if (sampleEl.tagName === 'level') {
              if (sampleEl.textContent !== 'Not detected') {
                if (sampleType === 'cellLine') {
                  this.hpaCellLines[sampleName] = null;
                } else if (sampleType === 'tissue') {
                  this.hpaTissues[sampleName] = null;
                }
                replicates.push(Math.log2(sampleEl.getAttribute('tpm') + 1));
              }
            } else {
              sampleName = sampleEl.textContent;
              // sampleType is cell line or tissue AFAIK
              sampleType = sampleEl.tagName;
            }
          }
          // Now take median in case of replicates
          replicates = replicates.sort((a, b) => a - b);
          const middle = Math.floor(replicates.length / 2);
          const geneExpression = { name: sampleName, type: sampleType };
          if (!replicates.length) {
            geneExpression.value = null;
            geneExpression.color = 'whitesmoke';
          } else if (replicates.length % 2 === 0) {
            geneExpression.value = (replicates[middle] + replicates[middle - 1]) / 2;
          } else {
            geneExpression.value = replicates[middle];
          }
          if (geneExpression.value) {
            if (geneExpression.value <= 1) {
              geneExpression.color = 'lightgray';
            } else if (geneExpression.value <= 4) {
              geneExpression.color = 'lightyellow';
            } else if (geneExpression.value <= 5.5) {
              geneExpression.color = 'orange';
            } else if (geneExpression.value <= 6.6) {
              geneExpression.color = 'red';
            } else {
              geneExpression.color = 'darkred';
            }
          }
          hpaGeneEx[genename].push(geneExpression);
        }
      }

      this.hpaTissues = Object.keys(this.hpaTissues).sort();
      this.hpaCellLines = Object.keys(this.hpaCellLines).sort();

      const rawElms2 = rawElms;

      for (const elid of Object.keys(rawElms2)) {
        // expressionElms[elid] = rawElms[elid];
        if (!rawElms2[elid].expressionLvl) {
          rawElms2[elid].expressionLvl = {};
        }
        if (!rawElms2[elid].expressionLvl.HPA) {
          rawElms2[elid].expressionLvl.HPA = {};
        }
        rawElms2[elid].expressionLvl.HPA.RNA = {};
        const HPARNAexp = rawElms2[elid].expressionLvl.HPA.RNA;
        if (hpaGeneEx[rawElms[elid].short]) {
          for (const tissue of hpaGeneEx[rawElms[elid].short]) {
            HPARNAexp[tissue.name] = tissue.color;
          }
        }
      }
      return rawElms2;
    },
    loadExpansion() {
      axios.get(`reaction_components/${this.selectedElmId}/with_interaction_partners`)
        .then((response) => {
          this.loading = false;
          this.errorMessage = null;

          const component = response.data.component;
          const reactions = response.data.reactions;
          const [newElms, newRels] = transform(component, this.selectedElmId, reactions);

          Object.assign(this.rawElms, newElms);
          Object.assign(this.rawRels, newRels);
          // this.rawElms = this.loadHPAData(this.rawElms);

          this.expandedIds.push(component.id);

          this.reactionCount = response.data.reactions.length;
          if (this.reactionCount > this.warnReactionCount) {
            this.showNetworkGraph = false;
            return;
          }
          this.showNetworkGraph = true;

          // The set time out wrapper enforces this happens last.
          setTimeout(() => {
            this.constructGraph(this.rawElms, this.rawRels);
          }, 0);
        })
        .catch((error) => {
          this.loading = false;
          switch (error.response.status) {
            case 406:
              this.errorMessage = this.$t('tooManyInteractionPartners');
              break;
            default:
              this.errorMessage = this.$t('unknownError');
          }
        });
    },
    highlightReaction() {
      let reactionId = null;
      for (const elm of this.elms) {
        if (this.selectedElmId === elm.id) {
          reactionId = elm.reaction;
          break;
        }
      }

      if (reactionId) {
        let eles = this.cy.collection();

        for (const rel of this.rels) {
          if (rel.reaction === reactionId) {
            const relationEle = this.cy.getElementById(rel.id);
            eles = eles.add(relationEle);

            const sourceEle = this.cy.getElementById(rel.source);
            eles = eles.add(sourceEle);

            const targetEle = this.cy.getElementById(rel.target);
            eles = eles.add(targetEle);
          }
        }

        const instance = this.cy.viewUtilities();
        instance.unhighlight(this.cy.elements());
        instance.highlight(eles);
        this.showGraphContextMenu = false;
      }
    },
    toggleGraphLegend() {
      this.showGraphLegend = !this.showGraphLegend;
      this.showColorPickerEnz = false;
      this.showColorPickerMeta = false;
    },
    redrawGraph(usingExpressionLevel, nodeType) {
      if (!usingExpressionLevel) {
        if ((nodeType === 'enzyme' && this.toggleEnzymeExpLevel) ||
          (nodeType === 'metabolite' && this.toggleMetaboliteExpLevel)) {
          return;
        }
      }
      const stylesheet = graph(this.rawElms, this.rawRels, this.nodeDisplayParams)[1];
      const cyzoom = this.cy.zoom();
      const cypan = this.cy.pan();
      this.cy.style(stylesheet);
      this.cy.viewport({
        zoom: cyzoom,
        pan: cypan,
      });
    },
    refreshGraph() {
      // this.cy.elements().remove();
      // this.cy.add(this.rawElms);
    },
    fitGraph() {
      setTimeout(() => {
        this.cy.fit();
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
    // this.switchSVG(compartmentID,
    constructGraph: function constructGraph(elms, rels, callback) {
      /* eslint-disable no-param-reassign */
      const [elements, stylesheet] = graph(elms, rels, this.nodeDisplayParams);
      const reactionComponentId = this.reactionComponentId;

      this.cy = cytoscape({
        container: this.$refs.cy,
        elements,
        style: stylesheet,
        layout: {
          // check 'cola' layout extension
          name: 'concentric',
          concentric(node) {
            if (node.degree() === 1) {
              return 1;
            }
            if (node.data().id === reactionComponentId) {
              return 10000;
            }
            if (node.data().type === 'enzyme') {
              return 100;
            }
            return 200;
          },
          fit: true,
        },
      });
      // this.cy.ready = this.cy.fit();
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
          'font-size': dim,
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
        contextMenuGraph.style.left = `${node.renderedPosition().x - 8}px`;
        contextMenuGraph.style.top = `${node.renderedPosition().y + 210}px`;
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
        if (this.selectedElmId !== '') {
          const instance = this.cy.viewUtilities();
          instance.highlight(this.cy.elements());
        }
        this.selectedElmId = '';
        this.selectedElm = null;
      });

      this.cy.on('tap', 'node', (evt) => {
        const node = evt.cyTarget;
        const elmId = node.data().id;

        this.selectedElmId = elmId;
        this.selectedElm = node.data();
        this.showGraphContextMenu = true;
        updatePosition(node);
      });

      this.cy.on('drag', 'node', (evt) => {
        const node = evt.cyTarget;
        if (this.selectedElmId === node.data().id && nodeInViewport(node)) {
          updatePosition(node);
        }
      });

      this.cy.on('tapstart', () => {
        this.showGraphContextMenu = false;
      });

      this.cy.on('tapdragout, tapend', () => {
        if (this.selectedElmId !== '') {
          const node = this.cy.getElementById(this.selectedElmId);
          if (!nodeInViewport(node)) {
            return;
          }
          this.showGraphContextMenu = true;
          updatePosition(node);
        }
      });
      console.log(callback);
      if (callback) {
        console.log('callback');
        callback();
      }
      /* eslint-enable no-param-reassign */
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
      const filename = `${this.reactionComponentId}_interaction_partners.graphml`;
      FileSaver.saveAs(blob, filename);
    },
    exportPNG: function exportPNG() {
      const a = document.createElement('a');
      const output = this.cy.png();

      a.href = output;
      a.download = `${this.reactionComponentId}_interaction_partners.png`;
      a.target = '_blank';
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },
    fixEnzSelectOption() {
      const option = document.getElementById('enz-select')
      .getElementsByTagName('optgroup')[0].childNodes[0];
      option.selected = 'selected';
      this.nodeDisplayParams.enzymeExpSample = option.label;
    },
    switchToExpressionLevel: function switchToExpressionLevel(
      componentType, expSource, expType, expSample) {
      // console.log(expSource);
      // console.log(expType);
      // console.log(expSample);
      let redraw = false;
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
                this.rawElms = this.loadHPAData(this.rawElms);
                this.expSourceLoaded[componentType].HPA = {};
                this.expSourceLoaded[componentType].HPA.RNA = true;
              } else {
                // load expression data from another source here
                console.log(expSample);
              }
              redraw = true;
            } else {
              redraw = true;
            }
          } else if (this.nodeDisplayParams.enzymeExpType !== expType) {
            this.nodeDisplayParams.enzymeExpType = expType;
            if (!this.expSourceLoaded.componentType.expSource.expType) {
              // sources that load only one specific exp type
              redraw = true;
            }
          } else if (this.nodeDisplayParams.enzymeExpSample !== expSample) {
            redraw = true;
          }
          this.nodeDisplayParams.enzymeExpSample = expSample;
        } else {
          this.nodeDisplayParams.enzymeExpSource = false;
          this.nodeDisplayParams.enzymeExpType = false;
          this.nodeDisplayParams.enzymeExpSample = false;
          redraw = true;
        }
      } else if (this.toggleMetaboliteExpLevel) {
        console.log(expSample);
        // load expression data for metabolite
      } else if (componentType === 'enzyme') {
        this.nodeDisplayParams.enzymeExpSource = false;
        this.nodeDisplayParams.enzymeExpType = false;
        this.nodeDisplayParams.enzymeExpSample = false;
      } else {
        this.nodeDisplayParams.metaboliteExpSource = false;
        this.nodeDisplayParams.metaboliteExpType = false;
        this.nodeDisplayParams.metaboliteExpSample = false;
      }
      if (redraw) {
        setTimeout(() => {
          if ((expSource && expType) && !expSample) {
            // fix option selection! because of optgroup?
            if (this.toggleEnzymeExpLevel) {
              this.fixEnzSelectOption();
            }
          }
          this.redrawGraph(true);
        }, 0);
      }
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
    viewReactionComponent: function viewReactionComponent(tabIndex) {
      EventBus.$emit('updateSelTab', tabIndex,
       this.selectedElm.real_id ? this.selectedElm.real_id : this.selectedElm.id);
    },
    chemicalFormula,
    chemicalName,
    chemicalNameExternalLink,
    visitLink,
    fetchXML,
    parseXML,
  },
};
</script>

<style lang='scss'>
.closest-interaction-partners {

  h1, h2 {
    font-weight: normal;
  }

  #cy {
    position: static;
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

  #graphOption {
    position: absolute;
    top: 12px;
    left: 12px;
    width: 220px;
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
    z-index: 999;

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
}

</style>
