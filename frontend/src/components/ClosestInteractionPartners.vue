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
          <div class="column" v-on:mouseleave="showMenuExport = false">
            <a class="button is-primary" v-on:click="showMenuExport = !showMenuExport">Export graph</a>
            <div v-show="showMenuExport" id="contextMenuExport" ref="contextMenuExport">
              <span class="button is-dark" v-on:click="exportGraphml">Graphml</span>
              <span class="button is-dark" v-on:click="exportPNG">PNG</span>
            </div>
          </div>
        </div>
        <div id="contextMenuGraph" ref="contextMenuGraph">
          <span class="button is-dark" v-on:click="navigate">Load interaction partners</span>
          <span class="button is-dark" v-on:click="loadExpansion">Expand interaction partners</span>
          <span class="button is-dark" v-on:click="highlightReaction">Highlight reaction</span>
          <span v-if="selectedElm && selectedElm.type === 'enzyme'" class="button is-dark">
            <a :href="selectedElm.hpaLink" target="_blank">View in HPA</a>
          </span>
          <span v-if="selectedElm && selectedElm.details && selectedElm.type === 'enzyme'" class="button is-dark">
            <a :href="selectedElm.details.uniprot_link" target="_blank">View in Uniprot</a>
          </span>
          <span v-if="selectedElm && selectedElm.details && selectedElm.type === 'metabolite'" class="button is-dark">
            <a :href="selectedElm.details.hmdb_link" target="_blank">View in HMDB</a>
          </span>
        </div>
        <div class="container columns">
          <div id="cy" ref="cy" class="column is-8">
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
// import C2S from 'canvas2svg';
import CytoscapeTable from 'components/CytoscapeTable';
import Loader from 'components/Loader';
import { default as transform } from '../data-mappers/closest-interaction-partners';
import { default as graph } from '../graph-stylers/closest-interaction-partners';
import { chemicalFormula, chemicalName, chemicalNameLink } from '../helpers/chemical-formatters';

export default {
  name: 'closest-interaction-partners',
  components: {
    CytoscapeTable,
    Loader,
  },
  data() {
    return {
      loading: true,
      errorMessage: null,
      title: '',
      rawRels: {},
      rawElms: {},
      reactionComponentId: '',
      selectedElmId: '',
      selectedElm: null,
      componentName: '',
      cy: null,
      tableStructure: [
        { field: 'type', colName: 'Type', modifier: null },
        { field: 'short', link: true, colName: 'Short name', modifier: chemicalNameLink },
        { field: 'long', colName: 'Long name', modifier: chemicalName },
        { field: 'formula', colName: 'Formula', modifier: chemicalFormula },
        { field: 'compartment', colName: 'Compartment', modifier: null },
      ],
      showMenuExport: false,
    };
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
          this.$refs.contextMenuGraph.style.display = 'none';
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

          const enzyme = response.data.enzyme;
          const reactions = response.data.reactions;

          const enzymeName = enzyme.short_name || enzyme.long_name;
          this.componentName = enzymeName;
          if (enzyme.enzyme) {
            const uniprotLink = enzyme.enzyme ? enzyme.enzyme.uniprot_link : null;
            const uniprotId = uniprotLink.split('/').pop();
            this.title = `Closest interaction partners | ${enzymeName}
              (<a href="${uniprotLink}" target="_blank">${uniprotId}</a>)`;
          } else {
            this.title = `Closest interaction partners | ${enzymeName}`;
          }

          [this.rawElms, this.rawRels] = transform(enzyme, this.reactionComponentId, reactions);
          this.selectedElm = this.rawElms[enzyme.id];

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
    loadExpansion() {
      axios.get(`reaction_components/${this.selectedElmId}/with_interaction_partners`)
        .then((response) => {
          this.loading = false;
          this.errorMessage = null;

          const enzyme = response.data.enzyme;
          const reactions = response.data.reactions;
          const [newElms, newRels] = transform(enzyme, this.selectedElmId, reactions);

          Object.assign(this.rawElms, newElms);
          Object.assign(this.rawRels, newRels);

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
        for (const elm of this.elms) {
          if (elm.reaction === reactionId) {
            const ele = this.cy.getElementById(elm.id);
            eles = eles.add(ele);
          }
        }

        const instance = this.cy.viewUtilities();
        instance.unhighlight(this.cy.elements());
        instance.highlight(eles);
        this.$refs.contextMenuGraph.style.display = 'none';
      }
    },
    highlightNode(elmId) {
      this.cy.nodes().deselect();
      const node = this.cy.getElementById(elmId);
      node.json({ selected: true });
      node.trigger('tap');
    },
    constructGraph: function constructGraph(elms, rels) {
      /* eslint-disable no-param-reassign */
      const [elements, stylesheet] = graph(elms, rels);
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
      contextMenuGraph.style.display = 'none';

      const updatePosition = (node) => {
        contextMenuGraph.style.left = `${node.renderedPosition().x - 8}px`;
        contextMenuGraph.style.top = `${node.renderedPosition().y + 210}px`;
      };

      this.cy.on('tap', () => {
        contextMenuGraph.style.display = 'none';
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
        contextMenuGraph.style.display = 'block';
        updatePosition(node);
      });

      this.cy.on('drag', 'node', (evt) => {
        const node = evt.cyTarget;
        if (this.selectedElmId === node.data().id) {
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

      a.href = window.URL.createObjectURL(new Blob([output], { type: 'text/xml' }));
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

    chemicalFormula,
    chemicalName,
    chemicalNameLink,
  },
};
</script>

<style lang='scss'>

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

</style>
