<template>
  <section :class="{ 'section extended-section' : !showViewer }">
    <div :class="{ 'container': !showViewer }">
      <template v-if="currentShowComponent">
        <keep-alive>
          <component v-bind:is="currentShowComponent"></component>
        </keep-alive>
      </template>
      <template v-else>
        <div class="columns">
          <div class="column has-text-centered">
            <h4 class="is-size-4 has-text-weight-bold">Advanced search all integrated GEMs</h4>
            <p class="has-text-weight-bold">Search metabolites, enzymes, reactions... through all the integrated models</p>
          </div>
        </div>
        <div>
          <div class="columns is-centered">
            <global-search :quickSearch=false :reroute=true :model="model" ref="globalSearch">
            </global-search>
          </div>
        </div>
        <br><hr>
        <div>
          <div class="columns has-text-centered">
            <div class="column">
              <h4 class="is-size-4 has-text-weight-bold">Explore a model: <i>{{ model }}</i></h4>
              <p class="has-text-weight-bold">
                Select a model and start browsing or navigate on the maps
              </p>
            </div>
          </div>
          <div class="columns is-centered">
            <div class="column is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile has-text-centered">
              <div class="dropdown is-hoverable dropdown-trigger">
                <button class="button is-medium is-fullwidth" aria-haspopup="true" aria-controls="dropdown-menu">
                  <span>Model: <a class="tag is-primary has-text-weight-bold is-medium">{{ models[model].short_name }}</a></span>
                  <span class="icon is-small">
                    <i class="fa fa-angle-down" aria-hidden="true"></i>
                  </span>
                </button>
                <div class="dropdown-menu is-size-2" id="dropdown-menu" role="menu">
                  <div class="dropdown-content">
                    <a class="dropdown-item has-text-centered is-size-6"
                      v-for="model, k in models"
                      @click="selectModel(model.database_name)" v-html="getModelDescription(model)">
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <br>
          <div id="toolsSelect" class="columns">
            <template v-for="tool in explorerTools">
              <div class="column">
                <router-link :to="{ path: `${tool.url}/${model}` }">
                  <div class="card">
                    <header class="card-header">
                      <p class="card-header-title is-size-5">{{ tool.name }}</p>
                    </header>
                    <div class="card-content">
                      <div class="content">
                          <img :src="tool.img" />
                      </div>
                    </div>
                  </div>
              </router-link>
              </div>
            </template>
          </div>
        </div>
      </template>
      </div>
    </div>
  </section>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import GemBrowser from 'components/explorer/GemBrowser';
import MapViewer from 'components/explorer/MapViewer';
import GlobalSearch from 'components/explorer/GlobalSearch';
import SearchTable from 'components/explorer/SearchTable';
import { idfy } from '../helpers/utils';
import { default as EventBus } from '../event-bus';
import { default as messages } from '../helpers/messages';

export default {
  name: 'explorer',
  components: {
    GemBrowser,
    MapViewer,
    GlobalSearch,
    SearchTable,
  },
  data() {
    return {
      /* eslint-disable global-require*/
      explorerTools: [
        { name: messages.gemBrowserName,
          img: require('../assets/gemBrowser2.png'),
          url: '/explore/gem-browser',
        },
        { name: messages.mapViewerName,
          img: require('../assets/mapViewer2.png'),
          url: '/explore/map-viewer',
        },
      ],
      model: 'hmr2',
      models: { hmr2: { short_name: '' }, hmr2n: { short_name: '' } },
      showViewer: false,
      currentShowComponent: '',

      compartments: {},
      compartmentStats: {},
      compartmentLetters: {},

      errorMessage: '',
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  beforeRouteUpdate(to, from, next) {
    this.setup();
    next();
  },
  created() {
    this.setup();
    this.getModelList();
    this.loadCompartmentData(this.model);

    EventBus.$on('requestViewer', (type, name, ids, forceReload) => {
      this.displayViewer();
      EventBus.$emit('showAction', type, name, ids, forceReload);
    });
    EventBus.$on('showMapViewer', () => {
      this.displayViewer();
    });
    EventBus.$on('showGemBrowser', () => {
      this.displayBrowser();
    });

    EventBus.$on('navigateTo', (tool, model, type, id) => {
      // console.log(`on explorer navigateTo ${tool} ${type} ${id}`);
      if (tool === 'GEMBrowser') {
        this.$router.push(`/explore/gem-browser/${model}/${type}/${idfy(id)}`);
      } else if (tool === 'MapViewer') {
        this.$router.push(`/explore/map-viewer/${model}/`);
      }
    });

    $('body').on('click', 'td m', function f() {
      if (!($(this).hasClass('cms'))) {
        EventBus.$emit('GBnavigateTo', 'metabolite', $(this).attr('class'));
      }
    });
    $('body').on('click', 'span.rcm', function f() {
      EventBus.$emit('GBnavigateTo', 'metabolite', $(this).attr('id'));
    });
    $('body').on('click', 'span.rce', function f() {
      EventBus.$emit('GBnavigateTo', 'enzyme', $(this).attr('id'));
    });
  },
  methods: {
    setup() {
      this.model = this.$route.params.model || 'hmr2';
      if (this.$route.name === 'search') {
        this.displaySearch();
      } else if (this.$route.name === 'viewer' ||
       this.$route.name === 'viewerCompartment' ||
        this.$route.name === 'viewerSubsystem') {
        this.displayViewer();
      } else if (this.$route.name === 'browser' || this.$route.name === 'browserRoot') {
        this.displayBrowser();
      } else {
        EventBus.$emit('destroy3Dnetwork');
        this.showViewer = false;
        this.currentShowComponent = '';
      }
    },
    loadCompartmentData(model) {
      axios.get(`${model}/compartment/`)
      .then((response) => {
        this.compartmentStats = {};
        this.compartmentLetters = {};
        for (const c of response.data) {
          this.compartmentLetters[c.letter_code] = c.name_id;
          this.compartmentStats[c.name_id] = c;
        }
      })
      .catch((error) => {
        switch (error.response.status) {
          default:
            this.errorMessage = messages.unknownError;
        }
      });
    },
    getModelList() {
      // get models list
      axios.get('models/')
        .then((response) => {
          const models = {};
          for (const model of response.data) {
            models[model.database_name] = model;
          }
          this.models = models;
        })
        .catch(() => {
          this.errorMessage = messages.unknownError;
        });
    },
    getModelDescription(model) {
      return `<div>${model.short_name} - ${model.name}<div>
      <div class="has-text-grey">
        ${model.reaction_count} reactions -
        ${model.metabolite_count} metabolites -
        ${model.enzyme_count} enzymes
      </div>`;
    },
    selectModel(model) {
      if (model !== this.model) {
        this.loadCompartmentData(model);
      }
      this.model = model;
      EventBus.$emit('modelSelected', this.models[this.model].short_name);
    },
    displayBrowser() {
      this.showViewer = false;
      this.currentShowComponent = 'GemBrowser';
    },
    displayViewer() {
      this.showViewer = true;
      this.currentShowComponent = 'MapViewer';
    },
    displaySearch() {
      this.showViewer = false;
      this.currentShowComponent = 'SearchTable';
    },
    getCompartmentNameFromLetter(l) {
      return this.compartmentLetters[l];
    },
    formatSpan(currentVal, index, array, elements, addComp) {
      const regex = /([0-9]+ )?(.+)\[([a-z]{1,3})\]/g;
      const match = regex.exec(currentVal);
      if (!addComp) {
        return `${match[1] ? match[1] : ''}<m class="${elements[index]}">${match[2]}</m>`;
      }
      return `${match[1] ? match[1] : ''}<m class="${elements[index]}">${match[2]}</m>
        <span class="sc" title="${this.compartmentLetters[match[3]]}">${match[3]}</span>`;
    },
    reformatChemicalReactionLink(reaction) {
      if (reaction === null) {
        return '';
      }
      const addComp = reaction.compartment.includes('=>');
      let eqArr = null;
      if (reaction.is_reversible) {
        eqArr = reaction.equation.split(' &#8660; ');
      } else {
        eqArr = reaction.equation.split(' &#8658; ');
      }
      if (eqArr.length === 1) {
        eqArr = reaction.equation.split(' => ');
      }
      const idEqArr = reaction.id_equation.split(' => ');
      let reactants = '';
      let products = '';
      if (idEqArr[0]) {
        const idReactants = idEqArr[0].split(' + ');
        reactants = eqArr[0].split(' + ').map(
          (x, i, a) => this.formatSpan(x, i, a, idReactants, addComp)
        ).join(' + ');
      }
      if (idEqArr[1]) {
        const idProducts = idEqArr[1].split(' + ');
        products = eqArr[1].split(' + ').map(
          (x, i, a) => this.formatSpan(x, i, a, idProducts, addComp)
        ).join(' + ');
      }

      if (reaction.is_reversible) {
        return `${reactants} &#8660; ${products}`;
      }
      return `${reactants} &#8658; ${products}`;
    },
  },
};

</script>

<style lang="scss">

#toolsSelect {
  .card {
    p {
      justify-content: center;
    }
    border: solid 1px white;
    &:hover {
      border: solid 1px black;
    }
  }
}

.dropdown, .dropdown-trigger, #dropdown-menu {
  width: 100%;
}

</style>
