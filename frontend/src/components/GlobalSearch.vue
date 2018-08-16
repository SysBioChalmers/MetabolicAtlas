<template>
  <div class="column is-6">
    <div class="control">
      <div v-if="!quickSearch">Search across all GEMs</div>
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
        <div class="has-text-centered">
          <div class="tag">
            Results are restricted to the active GEM and limited to 50 per component - Click <a @click="goToSearchPage">&nbsp;Here&nbsp;</a> to get full results
          </div>
        </div>
        <div v-if="searchResults" class="searchGroupResultSection"
          v-for="k in resultsOrder" >
          <div v-for="r in searchResults[k]" class="searchResultSection">
            <div v-if="k === 'enzyme'">
              <b>Enzyme: </b> {{ r.name }}
              <label v-html="formatSearchResultLabel(r, searchTermString)"></label>
              <div class="columns">
                <div class="column">
                  <span
                    class="tag is-primary is-medium"
                    @click="goToTab('interaction', r.id)">
                    Closest interaction partners
                  </span>
                  <span class="tag is-primary is-medium"
                    @click="goToTab('enzyme', r.id)">
                    Enzyme
                  </span>
                  <span class="tag is-info is-medium is-pulled-right"
                    @click="viewOnMetabolicViewer(r.id, 'enzyme')">
                    View
                  </span>
                </div>
              </div>
            </div>
            <div v-else-if="k === 'metabolite'">
              <b>Metabolite: </b> {{ r.name }}
              <label v-html="formatSearchResultLabel(r, searchTermString)"></label>
              <div class="columns">
                <div class="column">
                  <span
                    class="tag is-primary is-medium"
                    @click="goToTab('interaction', r.id)">
                    Closest interaction partners
                  </span>
                  <span class="tag is-primary is-medium"
                    @click="goToTab('metabolite', r.id)">
                    Metabolite
                  </span>
                  <span class="tag is-info is-medium is-pulled-right"
                    @click="viewOnMetabolicViewer(r.id, 'metabolite')">
                    View
                  </span>
                </div>
              </div>
            </div>
            <div v-else-if="k === 'reaction'">
              <b>Reaction: </b> {{ r.id }} ‒ {{ r.equation }}
              <div class="columns">
                <div class="column">
                  <span
                    class="tag is-primary is-medium"
                    @click="goToTab('reaction', r.id)">
                    Reaction
                  </span>
                  <span class="tag is-info is-medium is-pulled-right"
                    @click="viewOnMetabolicViewer(r.id, 'reaction')">
                    View
                  </span>
                </div>
              </div>
            </div>
            <div v-else-if="k === 'subsystem'">
              <b>Subsystem: </b> {{ r.name }} ‒ {{ r.system }}
              <div class="columns">
                <div class="column">
                  <span
                    class="tag is-primary is-medium"
                    @click="goToTab('subsystem', r.name.toLowerCase())">
                    Subsystem
                  </span>
                  <span class="tag is-info is-medium is-pulled-right"
                    @click="viewOnMetabolicViewer(r.name.toLowerCase(), 'subsystem')">
                    View
                  </span>
                </div>
              </div>
            </div>
            <div v-else-if="k === 'compartment'">
              <b>Compartment: </b> {{ r.name }}
              <div class="columns">
                <div class="column">
                  <span class="tag is-info is-medium is-pulled-right"
                    @click="viewOnMetabolicViewer(r.name.toLowerCase(), 'compartment')">
                    View
                  </span>
                </div>
              </div>
            </div>
            <hr>
          </div>
        </div>
        <div v-show="showLoader" class="has-text-centered">
          <a class="button is-primary is-inverted is-outlined is-large is-loading"></a>
        </div>
        <div v-show="!showLoader && noResult" class="has-text-centered">
          {{ $t('searchNoResult') }}
        </div>
        <div v-show="!showLoader && !noResult">
          <div class="searchResultSection has-text-centered">
            <a @click="goToSearchPage()">Show more</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Loader from 'components/Loader';
import _ from 'lodash';
import { chemicalFormula } from '../helpers/chemical-formatters';
import { default as EventBus } from '../event-bus';
import { getCompartmentFromName } from '../helpers/compartment';


export default {
  name: 'global-search',
  props: {
    quickSearch: {
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
    };
  },
  watch: {
    // searchResults() {
    //   if (!this.quickSearch) {
    //     console.log('here');
    //     console.log(this.searchTermString);
    //     console.log(this.searchResults);
    //     console.log('-------------------------');
    //     this.$emit('updateResults', this.searchTermString, this.searchResults);
    //   }
    // },
  },
  created() {
    // init the global events
    EventBus.$on('hideSearchResult', () => {
      this.showResults = false;
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
      .catch((error) => {
        console.log(error);
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
      EventBus.$emit('updateSelTab', type, id);
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
      EventBus.$emit('requestViewer', type, name, '', []);
    },
    formatSearchResultLabel(c, searchTerm) {
      let s = `${c.short_name || c.long_name} (${c.compartment}`;
      if (c.formula) {
        s = `${s} | ${this.chemicalFormula(c.formula)})`;
      } else {
        s = `${s})`;
      }
      if (c.enzyme && c.enzyme.uniprot_acc &&
       c.enzyme.uniprot_acc.toLowerCase().includes(searchTerm.toLowerCase())) {
        s = `${s} ‒ Uniprot ACC: ${c.enzyme.uniprot_acc}`;
      } else if (c.metabolite) {
        if (c.metabolite.hmdb &&
          c.metabolite.hmdb.toLowerCase().includes(searchTerm.toLowerCase())) {
          s = `${s} ‒ HMDB: ${c.metabolite.hmdb}`;
        } else if (c.metabolite.hmdb_name &&
          c.metabolite.hmdb_name.toLowerCase().includes(searchTerm.toLowerCase())) {
          s = `${s} ‒ HMDB: ${c.metabolite.hmdb_name}`;
        } else if (c.metabolite.kegg &&
          c.metabolite.kegg.toLowerCase().includes(searchTerm.toLowerCase())) {
          s = `${s} ‒ Kegg: ${c.metabolite.kegg}`;
        }
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
      if (this.quickSearch) {
        this.goToSearchPage();
      } else if (this.searchTermString.length >= 2) {
        this.$emit('searchResults');
        this.search(this.searchTermString);
      }
    },
    chemicalFormula,
    getCompartmentFromName,
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
  max-height: 22rem;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  border: 1px solid lightgray;
  border-top: 0;
  margin-top: -2px;
  z-index: 30;

  hr {
    margin: 1rem 0;
  }

  .searchGroupResultSection:first-child {
    padding-top: 15px;
  }

  .searchResultSection {
    padding: 0 10px;

    label {
      font-style: italic;
    }

    span {
      cursor: pointer;
    }
  }
}


</style>