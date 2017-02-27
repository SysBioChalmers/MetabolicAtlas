<template>
  <div class="connected-metabolites">
    <h1 class="title is-1">Connected metabolites</h1>
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
    <table class="table is-bordered is-striped is-narrow">
      <thead>
        <tr>
          <th>Type</th>
          <th>Reaction ID</th>
          <th>Short name</th>
          <th>Long name</th>
          <th>Formula</th>
          <th>Compartment</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="elm in elms">
          <td>{{ elm.type }}</td>
          <td v-if="elm.type === 'reaction'">{{ elm.id }}</td>
          <td v-else-if="elm.type === 'enzyme'"> - </td>
          <td v-else>{{ elm.parentid }}</td>
          <td v-html="chemicalNameLink(elm.short)"></td>
          <td v-html="chemicalName(elm.long)"></td>
          <td v-html="chemicalFormula(elm.formula)"></td>
          <td>{{ elm.compartment }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';
import cytoscape from 'cytoscape';
import { default as regCose } from 'cytoscape-cose-bilkent';
import { default as transform } from '../data-mappers/connected-metabolites';
import { default as graph } from '../graph-stylers/connected-metabolites';

export default {
  name: 'connected-metabolites',
  data() {
    return {
      errorMessage: '',
      elms: [],
    };
  },
  methods: {
    load() {
      axios.get(`enzymes/${this.$route.params.enzyme_id}/connected_metabolites`)
        .then((response) => {
          this.errorMessage = '';

          const [elms, rels] = transform(response.data);
          this.elms = elms;
          const [elements, stylesheet] = graph(elms, rels);
          cytoscape({
            container: this.$refs.cy,
            elements,
            style: stylesheet,
            layout: {
              name: 'cose-bilkent',
              tilingPaddingVertical: 50,
              tilingPaddingHorizontal: 50,
            },
          });
        })
        .catch((error) => {
          this.errorMessage = error.message;
        });
    },
    chemicalFormula(value) {
      if (value === null) {
        return '';
      }
      return value.replace(/([0-9])/g, '<sup>$1</sup>');
    },
    chemicalName(value) {
      if (value === null) {
        return '';
      }
      return value.replace(/(\+)/g, '<sup>$1</sup>');
    },
    chemicalNameLink(value) {
      if (value === null) {
        return '';
      }

      return `<a
                target='new'
                href='https://pubchem.ncbi.nlm.nih.gov/compound/${value}'
              >${this.chemicalName(value)}</a>`;
    },
  },
  beforeMount() {
    regCose(cytoscape);
    this.load();
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

</style>
