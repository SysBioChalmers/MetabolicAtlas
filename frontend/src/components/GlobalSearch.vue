<template>
  <div class="column" v-bind:class="quickSearch ? 'is-7' : 'is-8'">
    <div class="control">
      <div id="input-wrapper">
        <input
          id="search"
          class="input"
          v-model="searchTermString"
          @input="searchDebounce"
          type="text"
          :placeholder="$t('searchPlaceholder')"
          v-on:keyup.enter="validateSearch()"
          v-on:keyup.esc="showResults = false"
          v-on:focus="showResults = true"
          ref="searchInput">
          <div id="text-input-alert" v-show="showSearchCharAlert">Type at least 2 char</div>
      </div>
      <div v-if="quickSearch" id="searchResults" v-show="showResults && searchTermString.length > 1">
        <div v-if="searchResults" v-for="v, k in searchResults" class="searchGroupResultSection">
          <div v-for="r in v" class="searchResultSection">
            <div v-if="k === 'reactionComponent'">
              <div v-show="r.component_type == 'enzyme'">
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
              <div v-show="r.component_type == 'metabolite'">
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
            </div>
            <div v-else-if="k === 'compartment'">
              <strong>Compartment: </strong> {{ r.name }}
              <div>
                <span class="tag is-primary is-medium"
                  @click="viewCompartment(getCompartmentFromName(r.name.toLowerCase()).compartmentID)">
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
  },
  components: {
    Loader,
  },
  data() {
    return {
      errorMessage: '',
      searchResults: [],
      searchTermString: this.searchTerm,
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
    searchDebounce() {
      this.noResult = false;
      this.showSearchCharAlert = this.searchTermString.length === 1;

      if (!this.quickSearch) {
        return;
      }

      this.showLoader = true;
      this._.debounce(() => {
        if (this.searchTermString.length >= 2) {
          this.search(this.searchTermString);
        }
      }, 700)();
    },
    search(searchTerm) {
      const url = this.quickSearch ? `search/quick/${searchTerm}` : `search/${searchTerm}`;
      axios.get(url)
      .then((response) => {
        this.searchResults = response.data;
        this.noResult = true;
        for (const k of Object.keys(this.searchResults)) {
          if (this.searchResults[k].length) {
            this.showSearchCharAlert = false;
            this.noResult = false;
            break;
          }
        }
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
    viewCompartment(id) {
      console.log('test');
      this.goToTab('map', null);
      EventBus.$emit('showSVGmap', id, []);
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
        this.search(this.searchTermString);
      }
    },
    chemicalFormula,
    getCompartmentFromName,
  },
};
</script>

<style lang="scss">

#search {
  height: 38px;
}

#input-wrapper {
  position: relative; /* for absolute child element */
}

#text-input-alert {
  width: 150px;
  height: 38px;
  position: absolute; /* to align it to right and positon it over the input */
  top: 10px;
  right: 0;
  color: lightgrey;
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