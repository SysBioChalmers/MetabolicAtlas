<template>
  <div class="closest-interaction-partners">
    <h1 class="title is-1">Closest interaction partners</h1>
    <div class="container columns">
      <figure id="cy" ref="cy" class="column is-9"></figure>
      <div class="column content">
        <blockquote>
          We treat all chemical equations (eg reactions) form HMR2.0 as binary "interactions".
          This gives us the option of "zooming in" around a given ReactionComponent (species in SBML)
          (for example an enzyme from HPA).<br><br>
          This could be used to "determine" how important a given ReactionComponent is,
          and how a set of ReactionComponents interact and how their expression
          levels change between tissues.
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
import { default as transform } from '../data-mappers/closest-interaction-partners';
import { default as graph } from '../graph-stylers/closest-interaction-partners';

export default {
  name: 'closest-interaction-partners',
  data() {
    return {
      errorMessage: '',
      elms: [],
    };
  },
  methods: {
    load() {
      const reactionComponentId = this.$route.params.reaction_component_id;

      axios.get(`reaction_components/${reactionComponentId}`)
        .then((response) => {
          this.errorMessage = '';

          const e = response.data;

          axios.get(`reaction_components/${reactionComponentId}/interaction_partners`)
            .then((response2) => {
              this.errorMessage = '';

              const [elms, rels] = transform(e, reactionComponentId, response2.data);
              const [elements, stylesheet] = graph(elms, rels);
              cytoscape({
                container: this.$refs.cy,
                elements,
                style: stylesheet,
                layout: {
                  name: 'random',
                },
              });
            })
            .catch((error2) => {
              this.errorMessage = error2.message;
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
