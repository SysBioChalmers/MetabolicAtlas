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
      <div class="field">
        <p class="control">
          <input v-model="tableSearchTerm" class="input is-medium" type="text" placeholder="Search in table">
        </p>
      </div>
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
          <tr v-for="elm in matchingElms">
            <td>{{ elm.type }}</td>
            <td>{{ elm.reactionid }}</td>
            <td v-html="chemicalNameLink(elm.short)"></td>
            <td v-html="chemicalName(elm.long)"></td>
            <td v-html="chemicalFormula(elm.formula)"></td>
            <td>{{ elm.compartment }}</td>
          </tr>
        </tbody>
        <tbody class="unMatchingTable">
          <tr v-for="elm in unMatchingElms">
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
  data() {
    return {
      errorMessage: '',
      elms: [],
      matchingElms: [],
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
      this.sortedElms = this.elms.sort(compare(key, this.sortAsc ? 'asc' : 'desc'));
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
  watch: {
    tableSearchTerm() {
      this.updateTable();
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

th {
  cursor: pointer;
  user-select: none;
}

.unMatchingTable {
  opacity: 0.3;
}

</style>
