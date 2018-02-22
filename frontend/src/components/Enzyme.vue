<template>
  <div class="connected-metabolites">
    <div v-if="errorMessage" class="columns">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </div>
    <div v-show="!errorMessage">
      <div class="container columns">
        <div class="column is-5">
          <h3 class="title is-3">Enzyme | {{ enzymeName }}</h3>
        </div>
      </div>
      <div id="enzyme-details" class="reaction-table">
        <table v-if="enzyme && Object.keys(enzyme).length != 0" class="table main-table">
          <tr v-for="el in detailTableKey">
            <td v-if="el.display" class="td-key">{{ el.display }}</td>
            <td v-if="enzyme[el.name]">
              <span v-if="el.modifier" v-html="el.modifier(enzyme)">
              </span>
              <span v-else>
                {{ enzyme[el.name] }}
              </span>
            </td>
            <td v-else> - </td>
          </tr>
        </table>
      </div>
      <loader v-show="loading"></loader>
      <div v-show="!loading">
        <div v-show="reactions.length > 0">
          <loader v-show="loading"></loader>
          <reaction-table v-show="!loading" :reactions="reactions" :showSubsystem="true"></reaction-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import cytoscape from 'cytoscape';
import regCose from 'cytoscape-cose-bilkent';
import Sidebar from 'components/Sidebar';
import CytoscapeTable from 'components/CytoscapeTable';
import ReactionTable from 'components/ReactionTable';
import Loader from 'components/Loader';
// import { default as transform } from '../data-mappers/connected-metabolites';
// import { default as graph } from '../graph-stylers/connected-metabolites';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../helpers/chemical-formatters';
import { default as visitLink } from '../helpers/visit-link';

export default {
  name: 'enzyme',
  components: {
    Sidebar,
    CytoscapeTable,
    ReactionTable,
    Loader,
  },
  props: ['model'],
  data() {
    return {
      loading: true,
      cy: null,
      errorMessage: null,
      elms: [],

      id: '',
      selectedElmId: '',
      selectedElm: null,

      enzyme: {},
      enzymeName: '',
      tableStructure: [
        { field: 'type', colName: 'Type', modifier: false },
        { field: 'reactionid', colName: 'Reaction ID', modifier: false, rc: 'reaction', id: 'self' },
        { field: 'short', link: true, colName: 'Short name', modifier: false, rc: 'metabolite' },
        { field: 'long', colName: 'Long name', modifier: chemicalName },
        { field: 'formula', colName: 'Formula', modifier: chemicalFormula },
        {
          field: 'isCurrencyMetabolite',
          colName: 'Is currency metabolite',
          modifier: b => (b ? 'yes' : 'no'),
        },
        { field: 'compartment', colName: 'Compartment', modifier: null },
      ],
      detailTableKey: [
        { name: 'id', display: 'Identifier' },
        { name: 'enzymeName', display: 'Name' },
        { name: 'function', display: 'Function' },
        { name: 'long_name', display: 'Ensembl ID', modifier: this.reformatEnsblLink },
        { name: 'uniprot_acc', display: 'Uniprot ID', modifier: this.reformatUniprotLink },
        { name: 'ncbi', display: 'NCBI ID', modifier: this.reformatNCBIlink },
        { name: 'formula', display: 'Formula' },
        { name: 'compartment', display: 'Compartment' },

      ],

      tableSearchTerm: '',
      reactions: [],
      loadTime: 0,
      showGraphContextMenu: false,
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  computed: {
    filename() {
      return `ma_catalyzed_reaction_${this.enzymeName}`;
    },
    elmsInTable() {
      return this.elms.filter(elm => elm.type !== 'reaction' && elm.type !== 'enzyme');
    },
  },
  methods: {
    setup() {
      this.id = this.$route.query.id;
      this.selectedElmId = '';
      this.selectedElm = null;
      this.load();
    },
    highlightNode(elmId) {
      this.cy.nodes().deselect();
      const node = this.cy.getElementById(elmId);
      node.json({ selected: true });
      node.trigger('tap');
    },
    reformatList(l) {
      let output = '';
      if (l.length) {
        output = l.join('; ');
      } else {
        output = '-';
      }
      return output;
    },
    reformatEnsblLink(enzyme) {
      return `<a href="${enzyme.ensembl_link}" target="_blank">${enzyme.long_name}</a>`;
    },
    reformatUniprotLink(enzyme) {
      return `<a href="http://www.uniprot.org/uniprot/${enzyme.uniprot_acc}" target="_blank">${enzyme.uniprot_acc}</a>`;
    },
    reformatNCBIlink(enzyme) {
      return `<a href="https://www.ncbi.nlm.nih.gov/gene/${enzyme.ncbi}" target="_blank">${enzyme.ncbi}</a>`;
    },
    load() {
      this.loading = true;
      const startTime = Date.now();
      const enzymeId = this.id;
      axios.get(`${this.model}/enzymes/${enzymeId}/connected_metabolites`)
        .then((response) => {
          const endTime = Date.now();
          this.loadTime = (endTime - startTime) / 1000; // TODO: show load time in seconds

          this.loading = false;
          this.errorMessage = null;

          this.enzymeName = response.data.enzyme.short_name || response.data.enzyme.long_name;
          this.enzyme = response.data.enzyme;
          this.enzyme = $.extend(this.enzyme, response.data.enzyme.enzyme);
          this.enzyme.enzyme = null;
          this.enzyme.enzymeName = this.enzymeName;
          this.enzyme.long_name = response.data.enzyme.long_name;
          this.reactions = response.data.reactions;
        })
        .catch((error) => {
          this.loading = false;
          this.reactions = [];
          switch (error.response.status) {
            case 404:
              this.errorMessage = this.$t('notFoundError');
              break;
            default:
              this.errorMessage = this.$t('unknownError');
          }
        });
    },
    scrollTo(id) {
      const container = $('body, html');
      container.scrollTop(
        $(`#${id}`).offset().top - (container.offset().top + container.scrollTop())
      );
    },
    chemicalFormula,
    chemicalName,
    chemicalNameExternalLink,
    visitLink,
  },
  beforeMount() {
    regCose(cytoscape);
    this.setup();
  },
};

</script>

<style lang="scss">

h1, h2 {
  font-weight: normal;
}

.connected-metabolites {
  #cygraph-wrapper {
    position: relative;
  }

  #cy {
    position: static;
    margin: auto;
    height: 720px;
  }

  #sidebar {
    max-height: 720px;
    overflow-y: auto;
  }

  #contextMenuGraph {
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
}

</style>
