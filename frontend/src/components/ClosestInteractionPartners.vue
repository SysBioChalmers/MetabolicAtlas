<template>
  <div class="closest-interaction-partners">
    <title>{{title}}</title>
    <h3 class="title is-3" v-html="title"></h3>
    <div id="contextMenu" ref="contextMenu">
      <span class="button is-dark" v-on:click="navigate">Load interaction partners</span>
    </div>

    <div class="container columns">
      <div id="cy" ref="cy" class="column is-9">
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
            <div v-if="selectedElm.details.mass">
              <p class="label">Mass</p>
              <p>{{ selectedElm.details.mass }}</p>
              <br v-if="selectedElm.details.kegg">
            </div>
            <div v-if="selectedElm.details.kegg">
              <p class="label">Kegg</p>
              {{ selectedElm.details.kegg }}
            </div>
          </div>
        </div>
        <br>
        <p><a class="button is-dark is-outlined" v-on:click="exportGraph">Export to graphml</a></p>
        <p><a class="button is-dark is-outlined" v-on:click="exportPNG">Export to PNG</a></p>
        <blockquote>
          We treat all chemical equations (eg reactions) form HMR2.0 as binary "interactions".
          This gives us the option of "zooming in" around a given ReactionComponent (species in SBML)
          (for example an enzyme from HPA).<br><br>
          This could be used to "determine" how important a given ReactionComponent is,
          and how a set of ReactionComponents interact and how their expression
          levels change between tissues.
        </blockquote>
        <img >
      </div>
    </div>
    <cytoscape-table
      :structure="tableStructure"
      :elms="elms"
      :selected-elm-id="selectedElmId"
      @highlight="highlightNode($event)"
    ></cytoscape-table>
  </div>
</template>

<script>
import axios from 'axios';
import cytoscape from 'cytoscape';
import jquery from 'jquery';
import graphml from 'cytoscape-graphml';
// import C2S from 'canvas2svg';
import CytoscapeTable from 'components/CytoscapeTable';
import { default as regCose } from 'cytoscape-cose-bilkent';
import { default as transform } from '../data-mappers/closest-interaction-partners';
import { default as graph } from '../graph-stylers/closest-interaction-partners';
import { chemicalFormula, chemicalName, chemicalNameLink } from '../helpers/chemical-formatters';

export default {
  name: 'closest-interaction-partners',
  components: {
    CytoscapeTable,
  },
  data() {
    return {
      errorMessage: '',
      title: '',
      elms: [],
      reactionComponentId: '',
      selectedElmId: '',
      selectedElm: null,
      cy: null,
      tableStructure: [
        { field: 'type', colName: 'Type', modifier: null },
        { field: 'short', link: true, colName: 'Short name', modifier: chemicalNameLink },
        { field: 'long', colName: 'Long name', modifier: chemicalName },
        { field: 'formula', colName: 'Formula', modifier: chemicalFormula },
        { field: 'compartment', colName: 'Compartment', modifier: null },
      ],
    };
  },
  beforeMount() {
    regCose(cytoscape);
    graphml(cytoscape, jquery);
    this.setup();
  },
  methods: {
    setup() {
      this.reactionComponentId = this.$route.params.reaction_component_id
                                 || this.$route.query.reaction_component_id;
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
          this.$refs.contextMenu.style.display = 'none';
          this.selectedElmId = '';
          this.selectedElm = null;
        }
      );
    },
    load() {
      axios.get(`reaction_components/${this.reactionComponentId}/with_interaction_partners`)
        .then((response) => {
          this.errorMessage = '';

          const enzyme = response.data.enzyme;
          const reactions = response.data.reactions;

          const enzymeName = enzyme.short_name || enzyme.long_name;
          if (enzyme.enzyme) {
            const uniprotLink = enzyme.enzyme ? enzyme.enzyme.uniprot_link : null;
            const uniprotId = uniprotLink.split('/').pop();
            this.title = `Closest interaction partners | ${enzymeName}
              (<a href="${uniprotLink}" target="_blank">${uniprotId}</a>)`;
          } else {
            this.title = `Closest interaction partners | ${enzymeName}`;
          }

          const [elms, rels] = transform(enzyme, this.reactionComponentId, reactions);
          this.selectedElm = elms[enzyme.id];
          this.elms = Object.keys(elms).map(k => elms[k]);
          this.constructGraph(elms, rels);
        })
        .catch((error) => {
          this.errorMessage = error.message;
        });
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
          name: 'random',
        },
      });

      // const c = document.getElementsByTagName('canvas')[0];
      // const svgCxt = new C2S(c);
      // const scope = this;
      // const draw = function draw(ctx) {
      //   const r = scope.cy.renderer();
      //   r.drawElements(ctx, scope.cy.elements());
      // };

      // draw(svgCxt);
      // console.log(svgCxt.getSvg());

      const contextMenu = this.$refs.contextMenu;
      contextMenu.style.display = 'none';

      const updatePosition = (node) => {
        contextMenu.style.left = `${node.renderedPosition().x - 8}px`;
        contextMenu.style.top = `${node.renderedPosition().y + 210}px`;
      };

      this.cy.on('tap', () => {
        contextMenu.style.display = 'none';
        this.selectedElmId = '';
        this.selectedElm = null;
      });

      this.cy.on('tap', 'node', (evt) => {
        const node = evt.cyTarget;
        const elmId = node.data().id;

        this.selectedElmId = elmId;
        this.selectedElm = node.data();
        contextMenu.style.display = 'block';
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
    exportGraph: function exportGraph() {
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
        layoutby: 'random',
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
    exportPNG: function exportGraph() {
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

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

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
  overflow-y: scroll;
}

#contextMenu {
  position: absolute;
  z-index: 999;
}

</style>
