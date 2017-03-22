<template>
  <div class="connected-metabolites">
    <h3 class="title is-3">Connected metabolites</h3>
    <div class="container columns">
      <figure id="cy" ref="cy" class="column is-9"></figure>
      <div class="column content">
        <blockquote>
          Take an enzyme, in the form of an Ensembl Gene Identifier
          (for example ENSG00000164303 or <u>ENSG00000180011</u>)
          then it will find all reactions that this enzyme modifies,
          and for each of these reactions pull out the reactants (shape=heptagon)
          and the products (shape=octagon), eg the metabolites)
        </blockquote>
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
import CytoscapeTable from 'components/CytoscapeTable';
import { default as regCose } from 'cytoscape-cose-bilkent';
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
      tableStructure: [
        { field: 'type', colName: 'Type', modifier: null },
        { field: 'reactionid', colName: 'Reaction ID', modifier: null },
        { field: 'short', colName: 'Short name', modifier: chemicalNameLink },
        { field: 'long', colName: 'Long name', modifier: chemicalName },
        { field: 'formula', colName: 'Formula', modifier: chemicalFormula },
        { field: 'compartment', colName: 'Compartment', modifier: null },
      ],
      tableSearchTerm: '',
    };
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

          const [elms, rels] = transform(response.data);
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
          });

          this.cy.on('tap', 'node', (evt) => {
            const ele = evt.cyTarget;
            this.selectedElmId = ele.data().id;
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

</style>
