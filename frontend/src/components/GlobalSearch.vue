<template>
  <div class="column is-8">
    <div class="control">
      <div v-if="!quickSearch">Search across all GEMs</div>
      <div id="input-wrapper">
        <p class="control has-icons-right">
        <input
          id="search"
          class="input is-medium"
          v-model="searchTermString"
          @input="searchDebounce"
          type="text"
          :placeholder="$t('searchPlaceholder')"
          v-on:keyup.enter="validateSearch()"
          v-on:keyup.esc="showResults = false"
          v-on:focus="showResults = true"
          ref="searchInput">
          <span class="icon is-small is-right" v-show="showSearchCharAlert" style="width: 250px">
            Type at least 2 characters
          </span>
        </p>
      </div>
      <div v-if="quickSearch" id="searchResults" v-show="showResults && searchTermString.length > 1">
        <div class="has-text-centered">
          <div class="tag">
            Note: Results are restricted to the active GEM and limited to 50 per component - Hit Enter to get full results
          </div>
        </div>
        <div v-if="searchResults" class="searchGroupResultSection"
          v-for="k in resultsOrder" >
          <div v-for="r in searchResults[k]" class="searchResultSection">
            <div v-if="k === 'enzyme'">
              <strong>Enzyme: </strong> {{ r.name }}
              <label v-html="formatSearchResultLabel(r, searchTermString)"></label>
              <div>
                 <span
                  class="tag is-primary is-medium"
                  @click="goToTab('interaction', r.id)">
                  Closest interaction partners
                </span>
                <span class="tag is-primary is-medium"
                  @click="goToTab('enzyme', r.id)">
                  Enzyme
                </span>
              </div>
            </div>
            <div v-else-if="k === 'metabolite'">
              <strong>Metabolite: </strong> {{ r.name }}
              <label v-html="formatSearchResultLabel(r, searchTermString)"></label>
              <div>
                <span
                  class="tag is-primary is-medium"
                  @click="goToTab('interaction', r.id)">
                  Closest interaction partners
                </span>
                <span class="tag is-primary is-medium"
                  @click="goToTab('metabolite', r.id)">
                  Metabolite
                </span>
              </div>
            </div>
            <div v-else-if="k === 'reaction'">
              <strong>Reaction: </strong> {{ r.id }} ‒ {{ r.equation }}
              <div>
                <span
                  class="tag is-primary is-medium"
                  @click="goToTab('reaction', r.id)">
                  Reaction
                </span>
              </div>
            </div>
            <div v-else-if="k === 'subsystem'">
              <strong>Subsystem: </strong> {{ r.name }} ‒ {{ r.system }}
              <div>
                <span
                  class="tag is-primary is-medium"
                  @click="goToTab('subsystem', r.id)">
                  Subsystem
                </span>
              </div>
            </div>
            <div v-else-if="k === 'compartment'">
              <strong>Compartment: </strong> {{ r.name }}
              <div>
                <span class="tag is-primary is-medium"
                  @click="viewCompartment(r.name.toLowerCase())">
                  View
                </span>
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
    searchResults() {
      if (!this.quickSearch) {
        this.$emit('updateResults', this.searchTermString, this.searchResults);
      }
    },
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
        this.search(this.searchTermString);
      }
    }, 700),
    search(searchTerm) {
      const url = this.quickSearch ? `${this.model}/search/${searchTerm}` : `all/search/${searchTerm}`;
      axios.get(url)
      .then((response) => {
        const searchResults = response.data.reactionComponent.reduce((subarray, el) => {
          const arr = subarray;
          if (!arr[el.component_type]) { arr[el.component_type] = []; }
          arr[el.component_type].push(el);
          return arr;
        }, {});

        searchResults.reaction = response.data.reaction;
        searchResults.subsystem = response.data.subsystem;
        searchResults.compartment = response.data.compartment;

        // searchResults.metabolite = searchResults.reactionComponent.filter(
        // o => o.component_type === 'metabolite');
        // searchResults.enzyme = searchResults.reactionComponent.filter(
        // o => o.component_type === 'enzyme');
        // delete searchResults.reactionComponent;
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
      })
      .catch(() => {
        this.searchResults = [];
        this.noResult = true;
        this.showLoader = false;
      });
    },
    goToTab(type, id) {
      this.searchTerm = '';
      this.searchTermString = '';
      this.searchResults = [];
      EventBus.$emit('updateSelTab', type, id);
    },
    viewCompartment(name) {
      if (name === 'cytosol') {
        name = 'cytosol_1';  // eslint-disable-line no-param-reassign
      }
      EventBus.$emit('requestViewer', 'compartment', name, '', []);
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
  top: 40px;
  max-height: 300px;
  overflow-y: auto;
  width: 100%;
  border: 1px solid #64CC9A;
  border-top: 0;
  margin-top: -2px;
  z-index: 30;

  .searchGroupResultSection:first-child {
    padding-top: 15px;
  }

  .searchResultSection {
    margin-bottom: 10px;
    padding: 0 10px;
    background: white;

    label {
      font-style: italic;
    }

    span {
      cursor: pointer;
    }
  }

  .searchGroupResultSection:last-child {
    .searchResultSection:last-child {
      hr {
        display: none;
      }
    }
  }
}


</style>