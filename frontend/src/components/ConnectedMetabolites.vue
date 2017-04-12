<template>
  <div class="connected-metabolites">
    <h3 class="title is-3">Connected metabolites</h3>
    <div class="container columns">
      <figure id="cy" ref="cy" class="column is-9"></figure>
      <div id="sidebar" class="column content">
        <div v-if="selectedElm && selectedElm.details" class="card">
          <div class="card-content">
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
        <div v-else>
          Click on a reaction component for more details.
        </div>
        <br>
        <a href="/about#connectedmetabolites" target="_blank">More information</a>
      </div>
    </div>
    <div class="container">
      <cytoscape-table
        :structure="tableStructure"
        :elms="elms"
        :selected-elm-id="selectedElmId"
        @highlight="highlightNode($event)"
      ></cytoscape-table>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import cytoscape from 'cytoscape';
import regCose from 'cytoscape-cose-bilkent';
import CytoscapeTable from 'components/CytoscapeTable';
import { default as transform } from '../data-mappers/connected-metabolites';
import { default as graph } from '../graph-stylers/connected-metabolites';
import { chemicalFormula, chemicalName, chemicalNameLink } from '../helpers/chemical-formatters';

export default {
  name: 'connected-metabolites',
  components: {
    CytoscapeTable,
  },
  data() {
    return {
      cy: null,
      errorMessage: '',
      elms: [],
      selectedElmId: '',
      selectedElm: null,
      tableStructure: [
        { field: 'type', colName: 'Type', modifier: null },
        { field: 'reactionid', colName: 'Reaction ID', modifier: null },
        { field: 'short', link: true, colName: 'Short name', modifier: chemicalNameLink },
        { field: 'long', colName: 'Long name', modifier: chemicalName },
        { field: 'formula', colName: 'Formula', modifier: chemicalFormula },
        { field: 'compartment', colName: 'Compartment', modifier: null },
      ],
      tableSearchTerm: '',
    };
  },
  computed: {
    keggLink() {
      if (this.selectedElm
        && this.selectedElm.details
        && this.selectedElm.details.kegg
      ) {
        return `http://www.genome.jp/dbget-bin/www_bget?cpd:${this.selectedElm.details.kegg}`;
      }
      return '';
    },
  },
  methods: {
    highlightNode(elmId) {
      this.cy.nodes().deselect();
      const node = this.cy.getElementById(elmId);
      node.json({ selected: true });
      node.trigger('tap');
    },
    load() {
      const enzymeId = this.$route.params.enzyme_id || this.$route.query.enzyme_id;
      axios.get(`enzymes/${enzymeId}/connected_metabolites`)
        .then((response) => {
          this.errorMessage = '';

          console.log(response.data);
          const [elms, rels] = transform(response.data);
          this.selectedElm = elms[enzymeId];
          this.elms = elms;
          const [elements, stylesheet] = graph(elms, rels);
          this.cy = cytoscape({
            container: this.$refs.cy,
            elements,
            style: stylesheet,
            layout: {
              name: 'cose-bilkent',
              tilingPaddingVertical: 50,
              tilingPaddingHorizontal: 50,
            },
          });

          this.cy.on('tap', () => {
            this.selectedElmId = '';
            this.selectedElm = null;
          });

          this.cy.on('tap', 'node', (evt) => {
            const ele = evt.cyTarget;
            this.selectedElmId = ele.data().id;
            this.selectedElm = ele.data();
          });
        })
        .catch((error) => {
          this.errorMessage = error.message;
        });
    },
    chemicalFormula,
    chemicalName,
    chemicalNameLink,
  },
  beforeMount() {
    regCose(cytoscape);
    this.load();
  },
};

</script>

<style lang="scss">

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

</style>
