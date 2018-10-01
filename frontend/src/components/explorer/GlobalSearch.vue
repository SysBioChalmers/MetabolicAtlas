<template>
  <div class="column is-6">
    <div class="control">
      <div id="input-wrapper">
        <p class="control has-icons-right">
        <input
          id="search"
          class="input"
          v-model="searchTermString"
          @input="searchDebounce"
          type="text"
          :placeholder="$t('searchPlaceholder')"
          v-on:keyup.enter="!quickSearch ? validateSearch() : ''"
          v-on:keyup.esc="showResults = false"
          v-on:focus="showResults = true"
          ref="searchInput">
          <span class="icon is-small is-right" v-show="showSearchCharAlert" style="width: 250px">
            Type at least 2 characters
          </span>
        </p>
        <a v-if="quickSearch" @click="advancedSearch">Advanced search</a>
      </div>
      <div id="searchResults" v-show="quickSearch && showResults && searchTermString.length > 1" ref="searchResults">
        <div class="has-text-centered" v-show="searchResults.length !== 0 && !showLoader">
          <div class="notification is-medium is-paddingless">
            First 50 results per category from {{ getModelName() }} -&nbsp;<a @click="goToSearchPage">click here to load all</a> 
          </div>
        </div>
        <div class="resList" v-show="!showLoader">
          <div v-if="searchResults.length !== 0" class="searchGroupResultSection"
            v-for="k in resultsOrder" >
            <div v-for="r in searchResults[k]" class="searchResultSection">
              <div v-if="k === 'enzyme'">
                <b>Enzyme: </b>
                <label v-html="formatSearchResultLabel(k, r, searchTermString)"></label>
                <div class="columns">
                  <div class="column">
                    <span
                      class="button is-primary"
                      @click="goToTab('interaction', r.id)">
                      Closest interaction partners
                    </span>
                    <span class="button is-primary"
                      @click="goToTab('enzyme', r.id)">
                      Enzyme
                    </span>
                    <span class="button is-info is-pulled-right"
                      @click="viewOnMetabolicViewer(r.id, 'enzyme')" disabled>
                      View
                    </span>
                  </div>
                </div>
              </div>
              <div v-else-if="k === 'metabolite'">
                <b>Metabolite: </b>
                <label v-html="formatSearchResultLabel(k, r, searchTermString)"></label>
                <div class="columns">
                  <div class="column">
                    <span
                      class="button is-primary"
                      @click="goToTab('interaction', r.id)">
                      Closest interaction partners
                    </span>
                    <span class="button is-primary"
                      @click="goToTab('metabolite', r.id)">
                      Metabolite
                    </span>
                    <span class="button is-info is-pulled-right"
                      @click="viewOnMetabolicViewer(r.id, 'metabolite')" disabled>
                      View
                    </span>
                  </div>
                </div>
              </div>
              <div v-else-if="k === 'reaction'">
                <b>Reaction: </b>
                <label v-html="formatSearchResultLabel(k, r, searchTermString)"></label>
                <div class="columns">
                  <div class="column">
                    <span
                      class="button is-primary"
                      @click="goToTab('reaction', r.id)">
                      Reaction
                    </span>
                    <span class="button is-info is-pulled-right"
                      @click="viewOnMetabolicViewer(r.id, 'reaction')" disabled>
                      View
                    </span>
                  </div>
                </div>
              </div>
              <div v-else-if="k === 'subsystem'">
                <b>Subsystem: </b>
                <label v-html="formatSearchResultLabel(k, r, searchTermString)"></label>
                <div class="columns">
                  <div class="column">
                    <span
                      class="button is-primary"
                      @click="goToTab('subsystem', r.name.toLowerCase())">
                      Subsystem
                    </span>
                    <span class="button is-info is-pulled-right"
                      @click="viewOnMetabolicViewer(r.name.toLowerCase(), 'subsystem')" disabled>
                      View
                    </span>
                  </div>
                </div>
              </div>
              <div v-else-if="k === 'compartment'">
                <b>Compartment: </b>
                <label v-html="formatSearchResultLabel(k, r, searchTermString)"></label>
                <div class="columns">
                  <div class="column">
                    <span class="button is-info is-pulled-right"
                      @click="viewOnMetabolicViewer(r.name.toLowerCase(), 'compartment')" disabled>
                      View
                    </span>
                  </div>
                </div>
              </div>
              <hr>
            </div>
          </div>
        </div>
        <div v-show="showLoader" class="has-text-centered">
          <a class="button is-primary is-inverted is-outlined is-large is-loading"></a>
        </div>
        <div v-show="!showLoader && noResult" class="has-text-centered notification is-marginless">
          {{ $t('searchNoResult') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Loader from 'components/Loader';
import _ from 'lodash';
import { chemicalFormula, chemicalReaction } from '../../helpers/chemical-formatters';
import { default as EventBus } from '../../event-bus';

export default {
  name: 'global-search',
  props: {
    quickSearch: {
      default: false,
    },
    reroute: {
      default: false,
    },
    searchTerm: {
      default: '',
    },
    model: {
      default: '',
    },
  },
  components: {
    Loader,
  },
  data() {
    return {
      errorMessage: '',
      resultsOrder: ['metabolite', 'enzyme', 'reaction', 'subsystem', 'compartment'],
      searchResults: [],
      searchTermString: '',
      showSearchCharAlert: false,
      showResults: true,
      showLoader: false,
      noResult: false,

      itemKeys: {
        hmr2: {
          enzyme: ['gene_name'],
          reaction: ['id', 'equation'],
          metabolite: ['name', 'compartment'],
          subsystem: ['name', 'system'],
          compartment: ['name'],
        },
        yeast: {
          enzyme: ['gene_name'],
          reaction: ['id', 'equation'],
          metabolite: ['name', 'compartment'],
          subsystem: ['name', 'system'],
          compartment: ['name'],
        },
      },
    };
  },
  created() {
    // init the global events
    EventBus.$off('hideSearchResult');

    EventBus.$on('hideSearchResult', () => {
      this.showResults = false;
    });
    document.addEventListener('click', () => {
      EventBus.$emit('hideSearchResult');
    });
  },
  mounted() {
    this.$refs.searchResults.addEventListener('click', (e) => {
      e.stopPropagation();
    });
    this.$refs.searchInput.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  },
  methods: {
    searchDebounce: _.debounce(function e() {
      this.noResult = false;
      this.showSearchCharAlert = this.searchTermString.length === 1;
      if (!this.quickSearch) {
        return;
      }
      this.showLoader = true;
      if (this.searchTermString.length > 1) {
        this.showResults = true;
        this.search(this.searchTermString);
      }
    }, 700),
    search(searchTerm) {
      if (this.searchTermString !== searchTerm) {
        this.searchTermString = searchTerm;
      }
      const url = this.quickSearch ? `${this.model}/search/${searchTerm}` : `all/search/${searchTerm}`;
      axios.get(url)
      .then((response) => {
        const searchResults = {
          metabolite: [],
          enzyme: [],
          reaction: [],
          subsystem: [],
          compartment: [],
        };

        for (const model of Object.keys(response.data)) {
          const resultsModel = response.data[model];
          if (resultsModel.metabolite.length) {
            searchResults.metabolite = searchResults.metabolite.concat(
              resultsModel.metabolite.map(
              (e) => {
                const d = e; d.model = model; return d;
              }));
          }
          if (resultsModel.enzyme.length) {
            searchResults.enzyme = searchResults.enzyme.concat(
              resultsModel.enzyme.map(
              (e) => {
                const d = e; d.model = model; return d;
              }));
          }
          if (resultsModel.reaction.length) {
            searchResults.reaction = searchResults.reaction.concat(
              resultsModel.reaction.map(
              (e) => {
                const d = e; d.model = model; return d;
              }));
          }
          if (resultsModel.subsystem.length) {
            searchResults.subsystem = searchResults.subsystem.concat(
              resultsModel.subsystem).map(
              (e) => {
                const d = e; d.model = model; return d;
              });
          }
          if (resultsModel.compartment.length) {
            searchResults.compartment = searchResults.compartment.concat(
              resultsModel.compartment).map(
              (e) => {
                const d = e; d.model = model; return d;
              });
          }
        }

        this.noResult = true;
        for (const k of Object.keys(searchResults)) {
          if (searchResults[k].length) {
            this.showSearchCharAlert = false;
            this.noResult = false;
            break;
          }
        }
        this.searchResults = searchResults;
        this.showLoader = false;
        if (!this.quickSearch) {
          this.$emit('updateResults', this.searchTermString, this.searchResults);
        } else {
          this.$refs.searchResults.scrollTop = 0;
        }
      })
      .catch(() => {
        this.searchResults = [];
        this.noResult = true;
        this.showLoader = false;
        if (!this.quickSearch) {
          this.$emit('updateResults', this.searchTermString, this.searchResults);
        }
      });
    },
    goToTab(type, id) {
      this.searchTerm = '';
      this.searchTermString = '';
      this.searchResults = [];
      EventBus.$emit('GBnavigateTo', type, id);
    },
    advancedSearch() {
      this.$router.push({ name: 'search' });
    },
    viewOnMetabolicViewer(name, type) {
      if (type === 'compartment') {
        if (name === 'cytosol') {
          name = 'cytosol_1';  // eslint-disable-line no-param-reassign
        }
      }
      EventBus.$emit('navigateTo', 'mapViever', this.model, type, name);
    },
    formatSearchResultLabel(type, element, searchTerm) {
      if (!this.quickSearch) {
        return '';
      }
      let s = '';
      for (const key of this.itemKeys[this.model][type]) {
        if (element[key]) {
          if (key === 'equation') {
            s = `${s} ‒ ${chemicalReaction(element[key], element.is_reversible)}`;
          } else {
            s = `${s} ‒ ${element[key]}`;
          }
        }
      }
      if (!s.toLowerCase().includes(searchTerm.toLowerCase())) {
        // add info in the label containing the search string
        for (const k of ['hmdb_id', 'uniprot_id', 'ncbi_id', 'formula', 'pubchem_id', 'aliases', 'name']) {
          if (element[k] && element[k].toLowerCase().includes(searchTerm.toLowerCase())) {
            s = `${s} ‒ ${element[k]}`;
          }
        }
      }
      if (s.length !== 0) {
        return s.slice(2);
      }
      return s;
    },
    goToSearchPage() {
      this.$router.push({
        name: 'search',
        query: {
          term: this.searchTermString,
        },
      });
    },
    validateSearch() {
      if (this.quickSearch || this.reroute) {
        this.goToSearchPage();
      } else if (this.searchTermString.length >= 2) {
        this.$emit('searchResults');
        this.search(this.searchTermString);
      }
    },
    getModelName() {
      return this.$t(this.model);
    },
    chemicalFormula,
  },
};
</script>

<style lang="scss">

#input-wrapper {
  position: relative; /* for absolute child element */
}

#searchResults {
  background: white;
  position: absolute;
  top: 37px;
  overflow-x: hidden;
  width: 100%;
  border: 1px solid lightgray;
  border-top: 0;
  margin-top: -2px;
  z-index: 30;

  .resList {
      max-height: 22rem;
      overflow-y: auto;
  }

  hr {
    margin: 1rem 0;
  }

  .searchGroupResultSection:first-child {
    padding-top: 15px;
  }

  .searchResultSection {
    padding: 0 10px;
  }
}


</style>