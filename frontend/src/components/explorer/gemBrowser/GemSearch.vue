<template>
  <div v-if="model" id="gem-search-wrapper">
    <div class="field has-addons m-0">
      <p class="control">
        <span class="select">
          <select id="model-select" :value="searchModel.short_name"
                  @change="handleModelChange" @keyup.esc="handleClear()" @blur="blur()">
            <option v-for="m in models" :key="m.short_name">
              {{ m.short_name }}
            </option>
            <option>Global Search</option>
          </select>
        </span>
      </p>
      <p class="control is-expanded has-icons-right has-icons-left has-icons-right">
        <!-- eslint-disable max-len -->
        <input id="search" ref="searchInput"
               v-debounce:700="searchDebounce" data-hj-whitelist
               type="text" class="input"
               :placeholder="placeholder"
               :value="searchTermString"
               @keyup.esc="handleClear()"
               @focus="showResults = true"
               @blur="blur()">
        <span class="icon is-medium is-left"><i class="fa fa-search" /></span>
        <span v-show="showSearchCharAlert" class="has-text-info icon is-right" style="width: 270px">
          Type at least 2 characters
        </span>
        <span id="clear-search-icon" class="icon is-medium is-right has-text-grey-dark" @click="handleClearSearch()">
          <i class="fa fa-times-circle" />
        </span>
      </p>
    </div>
    <div v-show="showResults && searchTermString.length > 1" id="searchResults" ref="searchResults">
      <div v-show="searchResults.length !== 0 && !showLoader"
           class="notification is-large is-unselectable has-text-centered is-clickable py-1 mb-1"
           @mousedown="globalSearch()">
        Limited to 50 results per type. Click here to search all integrated GEMs
      </div>
      <div v-show="!showLoader" v-if="searchResults.length !== 0" class="resList">
        <template v-for="type in resultsOrder">
          <div v-for="(r, i2) in searchResults[type]" :key="`${r.id}-${i2}`" class="searchResultSection px-1 py-0">
            <hr v-if="i2 !== 0" class="m-0">
            <router-link class="is-clickable"
                         :to="{ name: type, params: { model: searchModel.short_name, id: r.id } }"
                         @click.native="handleClickResult">
              <span v-if="type === 'metabolite' || type === 'gene'" class="search-result-icons pr-1">
                <router-link class="is-clickable"
                             :to="{ name: type, params: { model: searchModel.short_name, id: r.id } }"
                             @click.native="handleClickResult">
                  <span class="icon is-medium is-left" title="Gem Browser"><i class="fa fa-table" /></span>
                </router-link>
                <router-link class="is-clickable"
                             :to="{ name: 'interaction', params: { model: searchModel.short_name, id: r.id } }"
                             @click.native="handleClickResult">
                  <span class="icon is-medium is-left" title="Interaction Partners"><i class="fa fa-connectdevelop" /></span>
                </router-link>
              </span>
              <b class="is-capitalized">{{ type }}: </b>
              <label class="is-clickable" v-html="formatSearchResultLabel(type, r, searchTermString)"></label>
            </router-link>
          </div>
          <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
          <hr v-if="searchResults[type] && searchResults[type].length !== 0" class="bhr p-0">
        </template>
      </div>
      <div v-show="showLoader" class="has-text-centered">
        <a class="button is-primary is-inverted is-outlined is-large is-loading"></a>
      </div>
      <div v-show="!showLoader && noResult" class="has-text-centered notification m-0">
        {{ messages.searchNoResult }}
        <div v-if="notFoundSuggestions.length !== 0">
          Do you mean:&nbsp;
          <template v-for="v in notFoundSuggestions">
            <a :key="v" class="suggestions has-text-link" @click.prevent="searchDebounce(v)">{{ v }}</a>&nbsp;
          </template>?
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import $ from 'jquery';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'GemSearch',
  props: {
    searchTerm: String,
    handleClear: Function,
  },
  data() {
    return {
      errorMessage: '',
      showSearchCharAlert: false,
      showResults: false,
      showLoader: false,
      noResult: false,
      messages,
      itemKeys: {
        gene: ['id', 'name'],
        reaction: ['id', 'equation'],
        metabolite: ['id', 'name', 'compartment'],
        subsystem: ['name', 'system'],
        compartment: ['name'],
      },
      notFoundSuggestions: [],
      searchModel: null,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      resultsOrder: state => state.search.categories,
      searchTermString: state => state.search.searchTermString,
    }),
    ...mapGetters({
      models: 'models/models',
      searchResults: 'search/categorizedAndSortedResults',
    }),
    placeholder() {
      return 'uracil, SULT1A3, ATP => cAMP + PPi, subsystem or compartment';
    },
  },
  async created() {
    await this.getIntegratedModelList();
  },
  methods: {
    async getIntegratedModelList() {
      await this.$store.dispatch('models/getModels');
      let modelKey = Object.keys(this.models)[0];
      if (this.$route.params && this.$route.params.model in this.models) {
        modelKey = this.$route.params.model;
      } else if (this.model) {
        modelKey = this.model.short_name;
        this.$router.replace({ params: { model: modelKey } });
      }
      this.$store.dispatch('models/selectModel', modelKey);
      this.searchModel = this.models[modelKey];
    },
    async handleModelChange(e) {
      e.preventDefault();
      const modelKey = e.target.value;

      if (modelKey === 'Global Search') {
        this.globalSearch();
      } else {
        this.searchModel = this.models[modelKey];
        await this.searchDebounce(this.searchTermString);
      }
    },
    async searchDebounce(searchTerm) {
      this.noResult = false;
      this.showSearchCharAlert = searchTerm.length === 1;
      this.$store.dispatch('search/setSearchTermString', searchTerm);

      const canSearch = searchTerm.length > 1;

      this.showLoader = canSearch;
      this.showResults = canSearch;
      if (canSearch) {
        await this.search(searchTerm);
      }
    },
    async search() {
      $('#search').focus();
      if (this.searchTermString.length < 2) {
        return;
      }

      try {
        const payload = {
          model: this.searchModel,
        };
        await this.$store.dispatch('search/search', payload);

        this.noResult = true;
        const keyList = Object.keys(this.searchResults);
        for (let i = 0; i < keyList.length; i += 1) {
          const k = keyList[i];
          if (this.searchResults[k].length) {
            this.showSearchCharAlert = false;
            this.noResult = false;
            break;
          }
        }
        this.showLoader = false;
        this.$refs.searchResults.scrollTop = 0;
      } catch (error) {
        this.$store.dispatch('search/clearSearchResults');
        this.noResult = true;
        if (error.response.headers.suggestions) {
          this.notFoundSuggestions = JSON.parse(error.response.headers.suggestions);
        } else {
          this.notFoundSuggestions = [];
        }
        this.showLoader = false;
      }
    },
    globalSearch() {
      this.handleClear();
      this.$router.push({ name: 'search', query: { term: this.searchTermString } });
    },
    formatSearchResultLabel(type, element, searchTerm) {
      const re = new RegExp(`(${searchTerm})`, 'ig');
      let s = '';
      this.itemKeys[type].filter(key => element[key]).forEach((key) => {
        // do not HL the compartment name
        s = key === 'compartment_str' ? `${s} ‒ ${element[key]}` : `${s} ‒ ${element[key].replace(re, '<b>$1</b>')}`;
      });
      if (s.length !== 0) {
        return s.slice(2);
      }
      return s;
    },
    handleClearSearch() {
      this.$store.dispatch('search/setSearchTermString', '');
      this.handleClear();
    },
    handleClickResult() {
      this.showResults = false;
      this.handleClear();
    },
    blur() {
      setTimeout(() => {
        if (document.getElementById('gem-search-wrapper').contains(document.activeElement) === false) {
          this.showResults = false;
          this.handleClear();
        } else if (document.getElementById('model-select').contains(document.activeElement) === false) {
          $('#search').focus();
        }
      });
    },
  },
};
</script>

<style lang="scss">

#gem-search-wrapper {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;

  .field, #searchResults {
    width: 100%;
    max-width: 800px;
  }

  .field {
    position: relative;
  }

  #clear-search-icon {
    cursor: pointer;
    pointer-events: auto;
  }

  #searchResults {
    background: white;
    position: absolute;
    top: 45px;
    overflow-x: hidden;
    width: 100%;
    border: 1px solid lightgray;
    border-top: 0;
    z-index: 30;

    .resList {
        max-height: 22rem;
        overflow-y: auto;
    }

    hr {
      &.bhr {
        margin: 5px 7px;
        border-top: 3px double #000000;
      }
    }
    .bhr:last-child {
      display: none;
    }

    .searchResultSection{
      > a {
        display: block;
        padding: 7px 0px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .search-result-icons a {
        &:first-child {
          color: $primary;
        }

        &:nth-child(2) {
          color: #A15786;
        }
      }
    }
  }
}

</style>
