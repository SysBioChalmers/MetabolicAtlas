<template>
  <div class="connected-metabolites">
    <h3 class="title is-3">Catalyzed reactions</h3>
    <loader v-show="loading"></loader>
    <div v-show="!loading">
      <div v-show="errorMessage" class="notification is-danger">{{ errorMessage }}</div>
      <div v-show="!errorMessage">
        <div v-show="reactions.length > 0">
          <div class="notification is-warning">{{ $t('tooManyReactions') }}</div>
          <reaction-table :reactions="reactions"></reaction-table>
        </div>
        <div v-show="reactions.length === 0">
          <div class="container columns">
            <figure id="cy" ref="cy" class="column is-8"></figure>
            <div id="sidebar" class="column content">
              <div v-if="selectedElm && selectedElm.type !== 'enzyme'" class="card">
                <div v-if="selectedElm.details" class="card">
                  <div class="card-content">
                    <div v-if="selectedElm.details.hmdb_description">
                      <p class="label">Description</p>
                      <p>{{ selectedElm.details.hmdb_description }}</p>
                      <br>
                    </div>
                    <div v-if="selectedElm.details.mass">
                      <p class="label">Mass</p>
                      {{ selectedElm.details.mass }}
                    </div>
                    <div v-if="selectedElm.details.kegg">
                      <p class="label">Kegg</p>
                      <a :href="keggLink" target="_blank">{{ selectedElm.details.kegg }}</a>
                    </div>
                    <div v-if="!selectedElm.details.mass &&
                               !selectedElm.details.catalytic_activity &&
                               !selectedElm.details.kegg">
                      {{ $t('noInfoAvailable') }}
                    </div>
                    <div v-else>
                      <br>
                      <button class="button" v-on:click="viewMetaboliteInfo()">More</button>
                    </div>
                  </div>
                </div>
                <div v-else>
                  <div class="card-content">
                    {{ $t('noInfoAvailable') }}
                  </div>
                </div>
              </div>
              <br>
              <a href="/about#connectedmetabolites" target="_blank">
                {{ $t('moreInformation') }}
              </a>
            </div>
            <div v-show="showGraphContextMenu" id="contextMenuGraph" ref="contextMenuGraph">
              <span v-if="selectedElm && selectedElm.type === 'enzyme'" class="button is-dark"
               v-on:click='visitLink(selectedElm.hpaLink, true)'>View in HPA
              </span>
              <span v-if="selectedElm && selectedElm.link && selectedElm.type === 'enzyme'" class="button is-dark"
                v-on:click='visitLink(selectedElm.link, true)'>View in Uniprot
              </span>
            </div>
          </div>
          <div class="container">
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
import cytoscape from 'cytoscape';
import regCose from 'cytoscape-cose-bilkent';
import CytoscapeTable from 'components/CytoscapeTable';
import ReactionTable from 'components/ReactionTable';
import Loader from 'components/Loader';
import { default as transform } from '../data-mappers/connected-metabolites';
import { default as graph } from '../graph-stylers/connected-metabolites';
import { chemicalFormula, chemicalName, chemicalNameLink } from '../helpers/chemical-formatters';
import { default as visitLink } from '../helpers/visit-link';

export default {
  name: 'connected-metabolites',
  components: {
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

      reactionComponentId: '',
      selectedElmId: '',
      selectedElm: null,

      enzymeName: '',
      tableStructure: [
        { field: 'type', colName: 'Type', modifier: null },
        { field: 'reactionid', colName: 'Reaction ID', modifier: null },
        { field: 'short', link: true, colName: 'Short name', modifier: chemicalNameLink },
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
      this.load();
    },
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
    filename() {
      return `ma_catalyzed_reaction_${this.enzymeName}`;
    },
    elmsInTable() {
      return this.elms.filter(elm => elm.type !== 'reaction' && elm.type !== 'enzyme');
    },
  },
  methods: {
    setup() {
      this.reactionComponentId = this.$route.query.reaction_component_id
                                  || this.$route.query.reaction_component_long_name;
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
      const startTime = Date.now();
      const enzymeId = this.reactionComponentId;

      axios.get(`enzymes/${enzymeId}/connected_metabolites`)
        .then((response) => {
          const endTime = Date.now();
          this.loadTime = (endTime - startTime) / 1000; // TODO: show load time in seconds

          this.loading = false;
          this.errorMessage = null;

          // If the response has only reacionts, it doesn't have an id in root object.
          if (response.data.id !== undefined) {
            this.reactions = [];

            const [elms, rels] = transform(response.data);
            this.enzymeName = response.data.short_name || response.data.long_name;
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
            this.cy.userZoomingEnabled(false);

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
              console.log(this.selectedElm);
            });

            this.cy.on('drag', 'node', (evt) => {
              const node = evt.cyTarget;
              if (this.selectedElmId === node.data().id) {
                updatePosition(node);
              }
            });

            this.cy.on('mouseover', 'node', (evt) => {
              const node = evt.cyTarget;
              console.log(node.data());
              let s;
              if (node.data().type === 'reactant_box') {
                s = 'Reactants';
              } else if (node.data().type === 'product_box') {
                s = 'Products';
              }
              node.css({
                content: s,
              });
            });

            this.cy.on('mouseout', 'node', (evt) => {
              const node = evt.cyTarget;
              node.css({
                content: '',
              });
            });

            this.cy.on('tapstart', () => {
              this.showGraphContextMenu = false;
            });

            this.cy.on('tapdragout, tapend', () => {
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
            this.reactions = response.data;
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
    viewMetaboliteInfo: function viewMetaboliteInfo() {
      this.$emit('updateSelTab', 4, this.reactionComponentId, this.selectedElmId);
    },
    chemicalFormula,
    chemicalName,
    chemicalNameLink,
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

#cy {
  position: static;
  margin: auto;
  height: 820px;
}

#sidebar {
  max-height: 820px;
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

</style>
