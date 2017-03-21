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
      <table-search
        :reset="resetTable"
        @search="searchTable($event)"
      ></table-search>
      <table class="table is-bordered is-striped is-narrow">
        <thead>
          <tr>
            <th
              v-for="col in tableColumns"
              @click="sortBy(col)"
            >{{ col }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="elm in matchingElms"
            :class="[{ 'highlight': isSelected(elm.id) }, '']"
            @click="highlightNode(elm.id)"
          >
            <td>{{ elm.type }}</td>
            <td>{{ elm.reactionid }}</td>
            <td v-html="chemicalNameLink(elm.short)"></td>
            <td v-html="chemicalName(elm.long)"></td>
            <td v-html="chemicalFormula(elm.formula)"></td>
            <td>{{ elm.compartment }}</td>
          </tr>
        </tbody>
        <tbody class="unMatchingTable">
          <tr
            v-for="elm in unMatchingElms"
            :class="[{ 'highlight': isSelected(elm) }, '']"
            @click="highlightNode(elm.id)"
          >
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
  </div>
</template>

<script>
import axios from 'axios';
import cytoscape from 'cytoscape';
import TableSearch from 'components/TableSearch';
import { default as regCose } from 'cytoscape-cose-bilkent';
import { default as transform } from '../data-mappers/connected-metabolites';
import { default as graph } from '../graph-stylers/connected-metabolites';
import { chemicalFormula, chemicalName, chemicalNameLink } from '../helpers/chemical-formatters';
import { default as compare } from '../helpers/compare';

const COL_TYPE = 'Type';
const COL_REACTION_ID = 'Reaction ID';
const COL_SHORT_NAME = 'Short name';
const COL_LONG_NAME = 'Long name';
const COL_FORMULA = 'Formula';
const COL_COMPARTMENT = 'Compartment';

export default {
  name: 'connected-metabolites',
  components: {
    TableSearch,
  },
  data() {
    return {
      cy: null,
      errorMessage: '',
      elms: [],
      matchingElms: [],
      selectedElmId: '',
      sortedElms: [],
      sortAsc: true,
      tableColumns: [
        COL_TYPE,
        COL_REACTION_ID,
        COL_SHORT_NAME,
        COL_LONG_NAME,
        COL_FORMULA,
        COL_COMPARTMENT,
      ],
      tableSearchTerm: '',
      unMatchingElms: [],
    };
  },
  methods: {
    isSelected(elmId) {
      return this.selectedElmId === elmId;
    },
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
          this.matchingElms = elms;
          this.sortedElms = elms;
          this.unMatchingElms = [];
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

            for (const elm of elms) {
              if (elm.id === ele.data().id) {
                this.selectedElmId = elm.id;
                break;
              }
            }
          });
        })
        .catch((error) => {
          this.errorMessage = error.message;
        });
    },
    resetTable() {
      this.sortedElms = this.elms;
      this.tableSearchTerm = '';
      this.selectedElmId = '';
      this.updateTable();
    },
    searchTable(term) {
      this.tableSearchTerm = term;
      this.updateTable();
    },
    sortBy(col) {
      let key = '';
      switch (col) {
        case COL_TYPE:
          key = 'type';
          break;
        case COL_REACTION_ID:
          key = 'reactionid';
          break;
        case COL_SHORT_NAME:
          key = 'short';
          break;
        case COL_LONG_NAME:
          key = 'long';
          break;
        case COL_FORMULA:
          key = 'formula';
          break;
        case COL_COMPARTMENT:
          key = 'compartment';
          break;
        default:
          key = 'type';
      }
      const elms = Array.prototype.slice.call(this.elms); // Do not mutate original elms;
      this.sortedElms = elms.sort(compare(key, this.sortAsc ? 'asc' : 'desc'));
      this.sortAsc = !this.sortAsc;
      this.updateTable();
    },
    updateTable() {
      if (this.tableSearchTerm === '') {
        this.matchingElms = this.sortedElms;
        this.unMatchingElms = [];
      } else {
        this.matchingElms = [];
        this.unMatchingElms = [];
        const t = this.tableSearchTerm.toLowerCase();

        for (const elm of this.sortedElms) {
          const matches = elm.type.toLowerCase().includes(t)
                          || (elm.id && elm.id.toLowerCase().includes(t))
                          || (elm.parentid && elm.parentid.toLowerCase().includes(t))
                          || elm.short.toLowerCase().includes(t)
                          || elm.long.toLowerCase().includes(t)
                          || elm.formula.toLowerCase().includes(t)
                          || (elm.compartment && elm.compartment.toLowerCase().includes(t));
          if (matches) {
            this.matchingElms.push(elm);
          } else {
            this.unMatchingElms.push(elm);
          }
        }
      }
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

th {
  cursor: pointer;
  user-select: none;
}

tr.highlight {
  background-color: #C5F4DD !important;
}

.unMatchingTable {
  opacity: 0.3;
}

</style>
