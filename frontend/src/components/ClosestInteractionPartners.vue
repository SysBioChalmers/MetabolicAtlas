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
            <h3 class="title is-3" v-html="title"></h3>
          </div>
          <div v-show="showNetworkGraph" class="column" v-on:mouseleave="showMenuExport = false">
            <a class="button is-primary" v-on:click="showMenuExport = !showMenuExport">Export graph</a>
            <div v-show="showMenuExport" id="contextMenuExport" ref="contextMenuExport">
              <span class="button is-dark" v-on:click="exportGraphml">Graphml</span>
              <span class="button is-dark" v-on:click="exportPNG">PNG</span>
            </div>
          </div>
        </div>
        <div v-show="showGraphContextMenu && showNetworkGraph" id="contextMenuGraph" ref="contextMenuGraph">
          <span class="button is-dark" v-on:click="navigate">Load interaction partners</span>
          <span v-show="expandedIds.indexOf(selectedElmId) === -1" 
          class="button is-dark" v-on:click="loadExpansion">Expand interaction partners</span>
          <span class="button is-dark" v-on:click="highlightReaction">Highlight reaction</span>
          <span v-show="selectedElm && selectedElm.type === 'enzyme'" class="button is-dark"
           v-on:click='visitLink(selectedElm.hpaLink, true)'>View in HPA
          </span>
          <span v-show="selectedElm && selectedElm.details && selectedElm.type === 'enzyme'" class="button is-dark"
            v-on:click='visitLink(selectedElm.details.uniprot_link, true)'>View in Uniprot
          </span>
          <span v-show="selectedElm && selectedElm.details && selectedElm.type === 'metabolite'" class="button is-dark"
            v-on:click='visitLink(selectedElm.details.hmdb_link, true)'>View in HMDB
          </span>
        </div>
        <div v-show="showNetworkGraph" class="container columns">
          <div class="column is-8">
            <div id="graphOption">
              <span class="button" v-bind:class="[{ 'is-active': showGraphLegend }, '']"
              v-on:click="toggleGraphLegend">Legend</span>
              <span class="button" v-on:click="zoomGraph(true)">+</span>
              <span class="button" v-on:click="zoomGraph(false)">-</span>
              <span class="button" v-on:click="fitGraph()">fit</span>
            </div>
            <div v-show="showGraphLegend" id="contextGraphLegend" ref="contextGraphLegend">
              <button class="delete" v-on:click="toggleGraphLegend"></button>
              <span class="label">Enzyme</span>
              <br>
              <span>Shape:</span>
              <div>
                <select v-model="nodeDisplayParams.enzymeNodeShape" v-on:change="redrawGraph()">
                  <option>rectangle</option>
                  <option>roundrectangle</option>
                  <option>cutrectangle</option>
                  <option>ellipse</option>
                  <option>rectangle</option>
                  <option>triangle</option>
                  <option>pentagon</option>
                  <option>hexagon</option>
                  <option>heptagon</option>
                  <option>octagon</option>
                  <option>star</option>
                  <option>diamond</option>
                  <option>vee</option>
                  <option>rhomboid</option>
                </select>
              </div>
              <span>Color:</span>
              <span class=color-span 
                v-bind:style="{ background: nodeDisplayParams.enzymeNodeColor.hex}"
                v-on:click="showColorPickerEnz = !showColorPickerEnz">
                <compact-picker v-show="showColorPickerEnz" 
                v-model="nodeDisplayParams.enzymeNodeColor" @input="redrawGraph()"></compact-picker>
              </span>
              <hr>
              <span class="label">Metabolite</span>
              <br>
              <span>Shape:</span>
              <div>
                <select v-model="nodeDisplayParams.metaboliteNodeShape" v-on:change="redrawGraph()">
                  <option>rectangle</option>
                  <option>roundrectangle</option>
                  <option>cutrectangle</option>
                  <option>ellipse</option>
                  <option>rectangle</option>
                  <option>triangle</option>
                  <option>pentagon</option>
                  <option>hexagon</option>
                  <option>heptagon</option>
                  <option>octagon</option>
                  <option>star</option>
                  <option>diamond</option>
                  <option>vee</option>
                  <option>rhomboid</option>
                </select>
              </div>
              <span>Color:</span>
               <span class=color-span 
                v-bind:style="{ background: nodeDisplayParams.metaboliteNodeColor.hex}"
                v-on:click="showColorPickerMeta = !showColorPickerMeta">
                <compact-picker v-show="showColorPickerMeta" 
                v-model="nodeDisplayParams.metaboliteNodeColor" @input="redrawGraph()"></compact-picker>
              </span>
            </div>
            <div id="cy" ref="cy">
            </div>
          </div>
          <div id="sidebar" class="column content">
            <div v-if="selectedElm && selectedElm.details" class="card">
              <div v-if="selectedElm.type === 'enzyme'" class="card-content">
                <div v-if="selectedElm.details.function">
                  <p class="label">Function</p>
                  <p>{{ selectedElm.details.function }}</p>
                  <br v-if="selectedElm.details.catalytic_activity">
                </div>
                <div v-if="selectedElm.details.catalytic_activity">
                  <p class="label">Catalytic Activity</p>
                  {{ selectedElm.details.catalytic_activity }}
                </div>
              </div>
              <div v-if="selectedElm.type === 'metabolite'" class="card-content">
                <div v-if="selectedElm.details.hmdb_description">
                  <p class="label">Description</p>
                  <p>{{ selectedElm.details.hmdb_description }}</p>
                  <br v-if="selectedElm.details.mass">
                </div>
                <div v-if="selectedElm.details.mass">
                  <p class="label">Mass</p>
                  <p>{{ selectedElm.details.mass }}</p>
                  <br v-if="selectedElm.details.kegg">
                </div>
                <div v-if="selectedElm.details.kegg">
                  <p class="label">Kegg</p>
                  <a :href="keggLink" target="_blank">{{ selectedElm.details.kegg }}</a>
                </div>
              </div>
            </div>
            <br>
            <a href="/about#closestpartners" target="_blank">
              {{ $t('moreInformation') }}
            </a>
          </div>
        </div>
        <div v-show="!showNetworkGraph" class="container columns">
          <div class="column is-4 is-offset-4 notification is-warning has-text-centered">
            <div>Warning: The query has returned too many reactions.<br>The graph has not been generated.</div>
            <span v-show="reactionsCount <= maxReactionCount" 
            class="button" v-on:click="constructGraph(rawElms, rawRels);">Show it anyway!</span>
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
// import C2S from 'canvas2svg';
import CytoscapeTable from 'components/CytoscapeTable';
import Loader from 'components/Loader';
import { default as transform } from '../data-mappers/closest-interaction-partners';
import { default as graph } from '../graph-stylers/closest-interaction-partners';
import { chemicalFormula, chemicalName, chemicalNameLink } from '../helpers/chemical-formatters';
import { default as visitLink } from '../helpers/visit-link';
import { default as convertGraphML } from '../helpers/graph-ml-converter';

export default {
  name: 'closest-interaction-partners',
  components: {
    CytoscapeTable,
    Loader,
    'compact-picker': Compact,
  },
  data() {
    return {
      loading: true,
      errorMessage: null,
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

      componentName: '',
      expandedIds: [],

      cy: null,
      tableStructure: [
        { field: 'type', colName: 'Type', modifier: null },
        { field: 'short', link: true, colName: 'Short name', modifier: chemicalNameLink },
        { field: 'long', colName: 'Long name', modifier: chemicalName },
        { field: 'formula', colName: 'Formula', modifier: chemicalFormula },
        { field: 'compartment', colName: 'Compartment', modifier: null },
      ],

      showMenuExport: false,
      showGraphLegend: false,
      showGraphContextMenu: false,
      showColorPickerEnz: false,
      showColorPickerMeta: false,

      nodeDisplayParams: {
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
    keggLink() {
      if (this.selectedElm
        && this.selectedElm.type === 'metabolite'
        && this.selectedElm.details
        && this.selectedElm.details.kegg
      ) {
        return `http://www.genome.jp/dbget-bin/www_bget?cpd:${this.selectedElm.details.kegg}`;
      }
      return '';
    },
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
          this.errorMessage = null;

          const component = response.data.component;
          const reactions = response.data.reactions;

          this.componentName = component.short_name || component.long_name;
          if (component.enzyme) {
            const uniprotLink = component.enzyme ? component.enzyme.uniprot_link : null;
            const uniprotId = uniprotLink.split('/').pop();
            this.title = `Closest interaction partners | ${this.componentName}
              (<a href="${uniprotLink}" target="_blank">${uniprotId}</a>)`;
          } else {
            this.title = `Closest interaction partners | ${this.componentName}`;
          }

          [this.rawElms, this.rawRels] = transform(component, this.reactionComponentId, reactions);
          this.selectedElm = this.rawElms[component.id];

          this.expandedIds = [];
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
          console.log('error:');
          console.log(error);
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
    redrawGraph() {
      const stylesheet = graph(this.elms, this.rels, this.nodeDisplayParams)[1];
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
        this.cy.fit();
      }, 500);
      this.minZoom = this.cy.zoom() / 2.0;
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
    constructGraph: function constructGraph(elms, rels) {
      /* eslint-disable no-param-reassign */
      const [elements, stylesheet] = graph(elms, rels, this.nodeDisplayParams);
      this.cy = cytoscape({
        container: this.$refs.cy,
        elements,
        style: stylesheet,
        layout: {
          // check 'cola' layout extension
          name: 'concentric',
        },
      });
      this.cy.userZoomingEnabled(false);
      this.fitGraph();

      window.pageYOffset = 0;
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;

      // const c = document.getElementsByTagName('canvas')[0];
      // const svgCxt = new C2S(c);
      // const scope = this;
      // const draw = function draw(ctx) {
      //   const r = scope.cy.renderer();
      //   r.drawElements(ctx, scope.cy.elements());
      // };

      // draw(svgCxt);
      // console.log(svgCxt.getSvg());

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
      /* eslint-enable no-param-reassign */
    },
    // TODO: refactor
    exportGraphml: function exportGraphml() {
      const a = document.createElement('a');
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

      a.href = window.URL.createObjectURL(new Blob([converted], { type: 'text/xml' }));
      a.download = `${this.reactionComponentId}_interaction_partners.graphml`;
      a.target = '_blank';
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
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

    chemicalFormula,
    chemicalName,
    chemicalNameLink,
    visitLink,
  },
};
</script>

<style lang='scss'>

h1, h2 {
  font-weight: normal;
}

#cy {
  position: absolute;
  margin: auto;
  height: 820px;
}

#sidebar {
  max-height: 820px;
  overflow-y: auto;
}

#contextMenuGraph, #contextMenuExport {
  position: absolute;
  z-index: 999;

  span {
    display: block;
    padding: 5px 10px;
    text-align: left;
    border-radius: 0;

    a {
      color: white;
    }
  }
}

#graphOption {
  position: absolute;
  top: 0;
  left: 0;
  width: 200px;
  height: 30px;
  z-index: 10;

  span {
    display: inline-block;
    margin-right: 5px;
  }
}

#contextGraphLegend {
  position: absolute;
  background: white;
  top: 32px;
  left: 0;
  width: 370px;
  height: auto;
  padding: 15px;
  border: 1px solid black;
  border-radius: 2px;
  z-index: 999;

  span, div {
    display: inline-block;
    margin-left: 20px;
  }
  .delete {
    position : absolute;
    right: 10px;
    top: 10px;
  }
  span.label {
    margin: 0;
  }
  span.color-span {
    height: 20px;
    width: 25px;
    border: 1px solid black;
    vertical-align: middle;
  }
  span.color-span:hover {
    cursor: pointer;
  }
}

</style>
