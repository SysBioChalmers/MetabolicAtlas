<template>
  <div id="mapSearch" class="overlay m-0 p-2" :class="[{'fullscreen' : fullscreen}]">
    <div class="control" :class="{ 'is-loading' : isSearching }">
      <input id="searchInput" data-hj-whitelist
             :class="searchInputClass"
             title="Exact search by id, name, alias. Press Enter for results" class="input"
             placeholder="Exact search by id, name, alias"
             :disabled="loading"
             :value="searchTerm"
             type="text" @input="e => handleChange(e.target.value)"
             @keyup.enter="e => search(e.target.value)" />
    </div>
    <template v-if="searchTerm && matches && matches.length !== 0 && totalSearchMatch !== 0">
      <span id="searchResCount" class="button has-text-dark"
            title="Click to center on current match"
            @click="centerViewOn(0)">
        {{ currentSearchMatch + 1 }} of {{ totalSearchMatch }}
      </span>
      <span class="button has-text-dark"
            title="Go to previous"
            @click="centerViewOn(-1)"><i class="fa fa-angle-left"></i></span>
      <span class="button has-text-dark"
            title="Go to next"
            @click="centerViewOn(1)"><i class="fa fa-angle-right"></i></span>
    </template>
    <template v-else-if="searchTerm && totalSearchMatch === 0 && haveSearched">
      <span class="has-text-white">{{ messages.searchNoResult }}</span>
    </template>
  </div>
</template>

<script>

import { mapState } from 'vuex';
import { debounce } from 'vue-debounce';
import { default as EventBus } from '@/event-bus';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'MapSearch',
  props: {
    matches: Array, // list of matched objects on the map/graph
    fullscreen: Boolean,
  },
  data() {
    return {
      errorMessage: '',

      prevSearchTerm: null,
      searchInputClass: '',
      isSearching: false,

      currentSearchMatch: 0,
      totalSearchMatch: 0,
      haveSearched: false,
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      searchTerm: state => state.maps.searchTerm,
      idsFound: state => state.maps.idsFound,
      loading: state => state.maps.loading,
    }),
  },
  watch: {
    matches() {
      if (!this.matches || this.matches.length === 0) {
        this.searchInputClass = this.haveSearched ? 'is-danger' : 'is-info';
        this.totalSearchMatch = 0;
      } else {
        this.searchInputClass = 'is-success';
        this.totalSearchMatch = this.matches.length;
      }
      this.currentSearchMatch = 0;
    },
    // workaround for the bug that 2D search bar can not type in text
    loading(now, before) {
      if (before === true && now === false) {
        this.focusOnInputSearch();
      }
    },
  },
  created() {
    this.search = debounce(this.search, 300);
    EventBus.$on('apply2DHPARNAlevels', () => {
      this.focusOnInputSearch();
    });
  },
  methods: {
    handleChange(term) {
      if (!term) {
        this.$emit('unHighlightAll', this.matches, 'schhl');
        this.totalSearchMatch = 0;
        this.currentSearchMatch = 0;
        this.searchInputClass = 'is-info';
        this.prevSearchTerm = null;
        this.$store.dispatch('maps/clearSearchTerm');
      }
      this.haveSearched = false;
    },
    reset() {
      // reset
      this.prevSearchTerm = null;
      this.totalSearchMatch = 0;
      this.currentSearchMatch = 0;
      this.searchInputClass = 'is-info';
    },
    async search(term) {
      this.$store.dispatch('maps/setIdsFound', []);

      if (!term) {
        this.searchInputClass = 'is-warning';
        return;
      }
      if (this.prevSearchTerm === term) {
        this.centerViewOn(1);
        return;
      }

      // get the IDs from the backend, then search in the SVG
      this.isSearching = true;
      try {
        const payload = { model: this.model, searchTerm: term };
        await this.$store.dispatch('maps/mapSearch', payload);
        this.totalSearchMatch = 0;
        this.currentSearchMatch = 0;
      } catch {
        this.searchInputClass = 'is-danger';
      } finally {
        this.isSearching = false;
        this.haveSearched = true;
        this.prevSearchTerm = term;
        this.$emit('searchOnMap', this.idsFound); // let the view call its own search function
      }
    },
    centerViewOn(position) {
      if (this.matches.length === 0) {
        return;
      }
      this.currentSearchMatch += position;
      if (this.currentSearchMatch < 0) {
        this.currentSearchMatch = this.totalSearchMatch - 1;
      } else if (this.currentSearchMatch > this.totalSearchMatch - 1) {
        this.currentSearchMatch = 0;
      }
      this.$emit('centerViewOn', this.matches[this.currentSearchMatch]);
    },
    focusOnInputSearch() {
      setTimeout(() => document.getElementById('searchInput').focus());
    },
  },
};
</script>

<style lang="scss">
  #mapSearch {
    top: 2rem;
    left: 20%;
    div {
      display: inline-block;
      vertical-align: middle;
    }
    span {
      margin-left: 5px;
    }
    #searchInput {
      display: inline-block;
      width: 20vw;
    }
    &.fullscreen {
      left: 30%;
      #searchInput {
        width: 30vw;
      }
    }
  }
</style>
