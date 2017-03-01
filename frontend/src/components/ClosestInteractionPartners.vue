<template>
  <div class="closest-interaction-partners">
    <title>{{title}}</title>
    <h1 class="title is-1">{{title}}</h1>
    <div id="contextMenu" ref="contextMenu">
      <span class="button is-dark" v-on:click="navigate">Load interaction partners</span>
    </div>

    <div class="container columns">
      <div id="cy" ref="cy" class="column is-9">
      </div>
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
          <th>Short name</th>
          <th>Long name</th>
          <th>Formula</th>
          <th>Compartment</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="elm in elms">
          <td>{{ elm.type }}</td>
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
import { chemicalFormula, chemicalName, chemicalNameLink } from '../helpers/chemical-formatters';

export default {
  name: 'closest-interaction-partners',
  data() {
    return {
      errorMessage: '',
      title: '',
      elms: [],
      reactionComponentId: '',
      selectedReactionComponentId: '',
      cy: null,
    };
  },
  beforeMount() {
    regCose(cytoscape);
    this.setup();
  },
  methods: {
    setup() {
      this.reactionComponentId = this.$route.params.reaction_component_id;
      this.title = `Closest interaction partners | ${this.reactionComponentId}`;
      this.load();
    },
    navigate() {
      this.$router.push(
        {
          name: 'closest-interaction-partners',
          params: { reaction_component_id: this.selectedReactionComponentId },
        },
        () => {
          this.setup();
        }
      );
    },
    load() {
      axios.get(`reaction_components/${this.reactionComponentId}/with_interaction_partners`)
        .then((response) => {
          this.errorMessage = '';

          const enzyme = response.data.enzyme;
          const reactions = response.data.reactions;

          const [elms, rels] = transform(enzyme, this.reactionComponentId, reactions);
          this.elms = Object.keys(elms).map(k => elms[k]);
          this.constructGraph(this, elms, rels);
        })
        .catch((error) => {
          this.errorMessage = error.message;
        });
    },
    constructGraph: (scope, elms, rels) => {
      /* eslint-disable no-param-reassign */
      const [elements, stylesheet] = graph(elms, rels);
      scope.cy = cytoscape({
        container: scope.$refs.cy,
        elements,
        style: stylesheet,
        layout: {
          name: 'random',
        },
      });

      const contextMenu = scope.$refs.contextMenu;
      const cyOff = scope.cy.container().getBoundingClientRect();
      contextMenu.style.display = 'none';

      const updatePosition = (node) => {
        contextMenu.style.left = `${node.renderedPosition().x - 10}px`;
        contextMenu.style.top = `${cyOff.top + 20 + node.renderedPosition().y}px`;
      };

      scope.cy.on('tap', () => {
        contextMenu.style.display = 'none';
      });
      scope.cy.on('tap', 'node', (evt) => {
        const node = evt.cyTarget;
        if (node.data().type === 'enzyme') {
          scope.selectedReactionComponentId = node.data().id;
          contextMenu.style.display = 'block';
          updatePosition(node);
        }
      });

      scope.cy.on('drag', 'node', (evt) => {
        const node = evt.cyTarget;
        if (node.data().type === 'enzyme' && scope.selectedReactionComponentId === node.data().id) {
          updatePosition(node);
        }
      });
      /* eslint-enable no-param-reassign */
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

#contextMenu {
  position: absolute;
  z-index: 999;
}

</style>
