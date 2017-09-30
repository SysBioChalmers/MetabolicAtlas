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
        <div class="column is-3">
          <nav class="breadcrumb is-small is-pulled-right" aria-label="breadcrumbs" v-if="reactions.length === 0">
            <ul>
              <li :class="{'is-active' : false }">
                <a @click="scrollTo('graph', 'enzyme-graph')">Reaction graph</a>
              </li>
              <li :class="{'is-active' : false }">
                <a @click="scrollTo('table', 'enzyme-table')">Reaction component table</a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
      <loader v-show="loading"></loader>
      <div v-show="!loading">
        <div v-show="reactions.length > 0">
          <div class="notification is-warning has-text-centered">{{ $t('tooManyReactions') }}</div>
          <loader v-show="loading"></loader>
          <reaction-table v-show="!loading" :reactions="reactions"></reaction-table>
        </div>
        <div v-show="reactions.length === 0">
          <div id="enzyme-graph" class="columns">
            <div id="cygraph-wrapper" class="column is-8">
              <div id="cy" ref="cy" class="is-8 card is-paddingless"></div>
              <div v-show="showGraphContextMenu" id="contextMenuGraph" ref="contextMenuGraph">
                <span v-if="selectedElm && selectedElm.type === 'enzyme'" class="button is-dark"
                 v-on:click='visitLink(selectedElm.hpaLink, true)'>View in HPA
                </span>
                <span v-if="selectedElm && selectedElm.link && selectedElm.type === 'enzyme'" class="button is-dark"
                  v-on:click='visitLink(selectedElm.link, true)'>View in Uniprot
                </span>
              </div>
            </div>
            <sidebar id="sidebar" :selectedElm="selectedElm" :view="'enzyme'"></sidebar>
          </div>
          <div id="enzyme-table" class="container">
            <cytoscape-table
              :structure="tableStructure"
              :elms="elmsInTable"
              :selected-elm-id="selectedElmId"
              :filename="filename"
              :sheetname="enzymeName"
              @highlight="highlightNode($event)"
            ></cytoscape-table>
          </div>
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
import { default as transform } from '../data-mappers/connected-metabolites';
import { default as graph } from '../graph-stylers/connected-metabolites';
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
  data() {
    return {
      loading: true,
      cy: null,
      errorMessage: null,
      elms: [],

      id: '',
      selectedElmId: '',
      selectedElm: null,

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
    load() {
      this.loading = true;
      const startTime = Date.now();
      const enzymeId = this.id;

      axios.get(`enzymes/${enzymeId}/connected_metabolites`)
        .then((response) => {
          const endTime = Date.now();
          this.loadTime = (endTime - startTime) / 1000; // TODO: show load time in seconds

          this.loading = false;
          this.errorMessage = null;

          // If the response has only reacionts, it doesn't have an id in root object.
          if (response.data.compartment !== undefined) {
            this.reactions = [];

            const [elms, rels] = transform(response.data);

            this.enzymeName = response.data.enzyme.short_name || response.data.enzyme.long_name;
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
            this.cy.userZoomingEnabled(false);

            this.selectedElm = this.cy.filter('node[type = "enzyme"]').data();

            const contextMenuGraph = this.$refs.contextMenuGraph;
            this.showGraphContextMenu = false;

            const updatePosition = (node) => {
              contextMenuGraph.style.left = `${node.renderedPosition().x + 20}px`;
              contextMenuGraph.style.top = `${node.renderedPosition().y + 20}px`;
            };

            const nodeInViewport = (node) => {
              if (node.renderedPosition().x < 0 || node.renderedPosition().x > this.cy.width()
                || node.renderedPosition().y < 0 || node.renderedPosition().y > this.cy.height()) {
                return false;
              }
              return true;
            };

            this.cy.on('tap', () => {
              this.showGraphContextMenu = false;
              this.selectedElmId = '';
              this.selectedElm = null;
            });

            this.cy.on('tap', 'node', (evt) => {
              const node = evt.cyTarget;
              const ele = evt.cyTarget;

              this.selectedElmId = ele.data().id;
              this.selectedElm = ele.data();
              this.showGraphContextMenu = true;
              updatePosition(node);
            });

            this.cy.on('drag', 'node', (evt) => {
              const node = evt.cyTarget;
              if (this.selectedElmId === node.data().id) {
                updatePosition(node);
              }
            });

            this.cy.on('tapstart', () => {
              this.showGraphContextMenu = false;
            });

            this.cy.on('tapdragout, tapend', 'node[type="enzyme"]', () => {
              if (this.selectedElmId !== '') {
                const node = this.cy.getElementById(this.selectedElmId);
                if (!nodeInViewport(node)) {
                  return;
                }
                this.showGraphContextMenu = true;
                updatePosition(node);
              }
            });
          } else {
            this.enzymeName = response.data.enzyme.short_name || response.data.enzyme.long_name;
            this.reactions = response.data.reactions;
          }
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
