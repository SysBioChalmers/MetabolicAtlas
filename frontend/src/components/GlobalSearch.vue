<template>
  <div class="column" v-bind:class="quickSearch ? 'is-7' : 'is-8'">
    <div class="control">
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
      <div v-if="quickSearch" id="searchResults" v-show="showResults && searchTermString.length > 1">
        <div v-if="searchResults.length > 0" v-for="r in searchResults" class="searchResultSection">
          <label class="title is-5" v-html="formatSearchResultLabel(r, searchTermString)"></label>
          <div>
            <span
              class="tag is-primary is-medium"
              @click="selectSearchResult(3, r.id)">
              Closest interaction partners
            </span>
            <span
              class="tag is-primary is-medium"
              v-show="r.component_type == 'enzyme'"
              @click="selectSearchResult(4, r.id)">
              Catalysed reactions
            </span>
            <span
              class="tag is-primary is-medium"
              v-show="r.component_type == 'metabolite'"
              @click="selectSearchResult(5, r.id)">
              Metabolite
            </span>
          </div>
          <hr>
        </div>
        <div v-if="searchResults.length == 0">
          <label class="title is-6">{{ $t('searchNoResult') }}</label>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { chemicalFormula } from '../helpers/chemical-formatters';

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
  data() {
    return {
      errorMessage: '',
      searchResults: [],
      searchTermString: this.searchTerm,
      showResults: true,
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
      if (!this.quickSearch) {
        return;
      }

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
      })
      .catch(() => {
        this.searchResults = [];
        // console.log(error);
      });
    },
    selectSearchResult(tabIndex, reactionComponentId) {
      this.searchTerm = '';
      this.searchTermString = '';
      this.searchResults = [];
      this.$router.push({
        query: {
          ...this.$route.query,
          reaction_component_id: reactionComponentId,
          tab: tabIndex,
        },
      });
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
    validateSearch() {
      if (this.quickSearch) {
        this.$router.push({
          name: 'search',
          query: {
            term: this.searchTermString,
          },
        });
      } else {
        this.search(this.searchTermString);
      }
    },
    chemicalFormula,
  },
};
</script>

<style lang="scss">

#search {
  height: 38px;
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
  z-index: 10;

  .resultSeparator:last-child {
    display: none;
  }

  .searchResultSection {
    margin-bottom: 10px;
    background: white;

    label {
      font-style: italic;
    }

    span {
      cursor: pointer;
    }
  }

  .searchResultSection:last-child hr {
    display: none;
  }
}


</style>