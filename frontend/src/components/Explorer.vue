<template>
  <section :class="{ 'section extended-section' : !showViewer }">
    <div :class="{ 'container': !showViewer }">
      <template v-if="showBrowser || showViewer || showSearch">
        <keep-alive>
          <gems-browser v-if="showBrowser" :model="model"></gems-browser>
          <gems-viewer v-if="showViewer" :model="model"></gems-viewer>
          <search-table v-if="showSearch"></search-table>
        </keep-alive>
      </template>
      <template v-else>
        <div class="columns">
            <div class="column has-text-centered">
              <h4 class="title is-4">Explore our models</h4>[<a @click="">Learn how</a>]
          </div>
        </div>
        <div class="box">
          <div class="columns">
            <div class="column has-text-centered has-text-weight-bold">
              Search metabolites, enzymes, reactions... through all our Models
            </div>
          </div>
          <div class="columns">
            <div class="column is-3">
            </div>
            <global-search
            :quickSearch=false
            :reroute=true
            :model="model"
            ref="globalSearch"></global-search>
          </div>
        </div>
        <div class="columns has-text-centered">
          <div class="column">
            OR
          </div>
        </div>
        <div class="box">
          <div class="columns has-text-centered">
            <div class="column">
              <div class="has-text-weight-bold">
                Select a model and start browsing or navigate on the maps
              </div>
            </div>
          </div>
          <div class="columns has-text-centered">
            <div class="column">
              <div class="dropdown is-hoverable">
                <div class="dropdown-trigger">
                  <button class="button" aria-haspopup="true" aria-controls="dropdown-menu">
                    <span>Model: <a class="tag is-info">{{ models[model].short_name }}</a></span>
                    <span class="icon is-small">
                      <i class="fa fa-angle-down" aria-hidden="true"></i>
                    </span>
                  </button>
                </div>
                <div class="dropdown-menu" id="dropdown-menu" role="menu">
                  <div class="dropdown-content">
                    <a class="dropdown-item"
                      v-for="model, k in models"
                      @click="selectModel(model.database_name)" v-html="getModelDescription(model)">
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="columns">
            <div class="column">
              <div class="card">
                <header class="card-header">
                  <p class="card-header-title">
                     Gems Browser
                  </p>
                </header>
                <div class="card-content">
                  <div class="content">
                    <a @click="goToGemsBrowser()">img browser</a>
                  </div>
                </div>
                <footer class="card-footer">
                </footer>
              </div>
            </div>
            <div class="column">
              <div class="card">
                <header class="card-header">
                  <p class="card-header-title">
                    Maps Viewer
                  </p>
                </header>
                <div class="card-content">
                  <div class="content">
                    <a @click="goToGemsViewer()">img map viewer</a>
                  </div>
                </div>
                <footer class="card-footer">
                </footer>
              </div>
            </div>
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
import GemsBrowser from 'components/explorer/GemsBrowser';
import GemsViewer from 'components/explorer/GemsViewer';
import GlobalSearch from 'components/explorer/GlobalSearch';
import SearchTable from 'components/explorer/SearchTable';
import { default as EventBus } from '../event-bus';


export default {
  name: 'explorer',
  components: {
    GemsBrowser,
    GemsViewer,
    GlobalSearch,
    SearchTable,
  },
  data() {
    return {
      model: 'hmr2',
      models: { hmr2: { short_name: '' }, hmr2n: { short_name: '' } },
      showBrowser: false,
      showViewer: false,
      showSearch: false,

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
    // console.log('BRU ex');
    this.setup();
    next();
  },
  // beforeMount() {
  //   this.setup();
  // },
  created() {
    this.setup();
    this.getModelList();
    this.loadCompartmentData(this.model);

    EventBus.$on('requestViewer', (type, name, secondaryName, ids) => {
      this.showGemsViewer = true;
      // console.log(`requestViewer ${type}, ${name}, ${secondaryName}, ${ids}`);
      EventBus.$emit('showAction', type, name, secondaryName, ids);
    });
    EventBus.$on('showGemsViewer', () => {
      this.displayViewer();
    });
    EventBus.$on('showGemsBrowser', () => {
      this.displayBrowser();
    });

    EventBus.$on('navigateTo', (tool, type, id) => {
      // console.log(`on explorer navigateTo ${tool} ${type} ${id}`);
      if (tool === 'gemsBrowser') {
        this.$router.push(`/Explore/browser/${this.model}/${type}/${id}`);
      } else if (tool === 'gemsViewer') {
        this.$router.push(`/Explore/viewer/${this.model}/`);
      }
    });

    $('body').on('click', 'td m', function f() {
      if (!($(this).hasClass('cms'))) {
        EventBus.$emit('GBnavigateTo', 'metabolite', $(this).attr('class'));
      }
    });
    // document.body.addEventListener('keyup', (e) => {
    //   if (e.keyCode === 27) {
    //     this.showGemsViewer = false;
    //   }
    // });
  },
  methods: {
    setup() {
      // console.log('exp route', this.$route);
      if (this.$route.name === 'search') {
        this.displaySearch();
      } else if (this.$route.name === 'viewer') {
        this.displayViewer();
      } else if (this.$route.name === 'browser' || this.$route.name === 'browserRoot') {
        this.displayBrowser();
      } else {
        this.showBrowser = false;
        this.showViewer = false;
        this.showSearch = false;
      }
    },
    loadCompartmentData(model) {
      axios.get(`${model}/compartments/`)
      .then((response) => {
        console.log(response);
        this.compartmentStats = {};
        this.compartmentLetters = {};
        for (const c of response.data) {
          this.compartmentLetters[c.letter_code] = c.name;
          this.compartmentStats[c.name] = c;
        }
      })
      .catch((error) => {
        switch (error.response.status) {
          default:
            this.errorMessage = this.$t('unknownError');
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
          this.errorMessage = this.$t('unknownError');
        });
    },
    getModelDescription(model) {
      return `<div>${model.short_name} - ${model.name}<div>
      <div class="has-text-grey">
        ${model.reaction_count} reactions -
        ${model.metabolite_count} metabolites -
        <br>${model.enzyme_count} enzymes
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
      this.showBrowser = true;
      this.showViewer = false;
      this.showSearch = false;
    },
    displayViewer() {
      this.showBrowser = false;
      this.showViewer = true;
      this.showSearch = false;
    },
    displaySearch() {
      this.showSearch = true;
      this.showBrowser = false;
      this.showViewer = false;
    },
    goToGemsBrowser() {
      this.$router.push(`/Explore/browser/${this.model}`);
    },
    goToGemsViewer() {
      this.$router.push(`/Explore/viewer/${this.model}`);
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
      const idReactants = idEqArr[0].split(' + ');
      const idProducts = idEqArr[1].split(' + ');
      const reactants = eqArr[0].split(' + ').map(
          (x, i, a) => this.formatSpan(x, i, a, idReactants, addComp)
        ).join(' + ');
      const products = eqArr[1].split(' + ').map(
          (x, i, a) => this.formatSpan(x, i, a, idProducts, addComp)
        ).join(' + ');

      if (reaction.is_reversible) {
        return `${reactants} &#8660; ${products}`;
      }
      return `${reactants} &#8658; ${products}`;
    },
  },
};

</script>

<style lang="scss">
</style>