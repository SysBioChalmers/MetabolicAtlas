<template>
  <div class="network-graph">
    <div class="columns">
      <div class="column is-3">
        <div class="tabs is-pulled-left is-toggle">
          <li class="is-active"><a><span>{{ $t('human') }}</span></a></li>
          <li><a><span>{{ $t('yeast') }}</span></a></li>
        </div>
      </div>
      <global-search
      :quickSearch=true
      ><global-search>
    </div>
    <br>
    <div class="tabs is-boxed">
     <ul>
       <li
         v-for="(tab, index) in tabs"
         :class="[{ 'is-active': isActive(index) }, { 'is-disabled': tab.isDisabled }]"
         :disabled="tab.isDisabled"
         @click="goToTab(index, reactionComponentID)"
       >
        <a :class="{ 'disabled': tab.isDisabled }"><span>{{ tab.title }}</span></a>
       </li>
     </ul>
   </div>
   <div v-if="errorMessage">
    {{ errorMessage }}
   </div>
   <div v-else>
      <metabolic-network v-if="selectedTab===1"></metabolic-network>
     <closest-interaction-partners v-if="selectedTab===3" 
      @updateSelTab="goToTab"></closest-interaction-partners>
     <connected-metabolites v-if="selectedTab===4" 
      @updateSelTab="goToTab"></connected-metabolites>
     <metabolite v-if="selectedTab===5"></metabolite>
   </div>
  </div>
</template>

<script>

import axios from 'axios';
import GlobalSearch from 'components/GlobalSearch';
import MetabolicNetwork from 'components/MetabolicNetwork';
import ClosestInteractionPartners from 'components/ClosestInteractionPartners';
import ConnectedMetabolites from 'components/ConnectedMetabolites';
import Metabolite from 'components/Metabolite';
import { default as EventBus } from '../event-bus';

export default {
  name: 'network-graph',
  components: {
    MetabolicNetwork,
    ClosestInteractionPartners,
    ConnectedMetabolites,
    Metabolite,
    GlobalSearch,
  },
  data() {
    return {
      selectedTab: 1,
      searchTerm: '',
      searchResults: [],
      errorMessage: '',
      reactionComponentID: '',
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  beforeMount() {
    // init the global event
    EventBus.$on('updateSelTab', (tabIndex, id) => {
      this.goToTab(tabIndex, id);
    });
    this.setup();
  },
  computed: {
    tabs() {
      let disabledTab4 = false;
      let disabledTab5 = false;
      if ([3, 4, 5].includes(this.selectedTab) && this.reactionComponentID) {
        disabledTab4 = this.reactionComponentID[0] === 'M';
        disabledTab5 = this.reactionComponentID[0] === 'E';
      }

      return [
        { title: this.$t('tab1title'), isDisabled: false },
        { title: this.$t('tab2title'), isDisabled: false },
        { title: this.$t('tab3title'), isDisabled: false },
        { title: this.$t('tab4title'), isDisabled: disabledTab4 },
        { title: this.$t('tab5title'), isDisabled: disabledTab5 },
        { title: this.$t('tab6title'), isDisabled: false },
      ];
    },
  },
  methods: {
    setup() {
      this.selectedTab = parseInt(this.$route.query.tab, 10) || 1;
      this.reactionComponentID = this.$route.query.reaction_component_id;
    },
    isActive(tabIndex) {
      return tabIndex + 1 === this.selectedTab;
    },
    goToTab(tabIndex, reactionComponentID) {
      this.reactionComponentID = reactionComponentID;
      if (this.tabs[tabIndex].isDisabled) {
        return;
      }

      if ([2, 3, 4].includes(this.tabIndex) && !reactionComponentID) {
        this.errorMessage = this.$t('noIDProvided');
        console.log(this.$children);
        // this.$children[0]
      } else {
        this.errorMessage = '';
      }

      this.selectedTab = tabIndex + 1;
      const fullQuery = {
        ...this.$route.query,
        tab: this.selectedTab,
      };
      if (reactionComponentID) {
        fullQuery.reaction_component_id = reactionComponentID;
      }
      this.$router.push({
        query: fullQuery,
      });
    },
    search() {
      if (this.searchTerm.length < 2) {
        return;
      }
      // make sure we serach a term of size 2
      const searchTerm = this.searchTerm;
      this._.debounce(() => {
        axios.get(`search/${searchTerm}`)
          .then((response) => {
            this.searchResults = response.data;
          })
          .catch(() => {
            this.searchResults = [];
            // console.log(error);
          });
      }, 500)();
    },
    selectSearchResult(tabIndex, reactionComponentID) {
      this.searchTerm = '';
      this.searchResults = [];
      this.goToTab(tabIndex, reactionComponentID);
    },
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
  top: 50px;
  max-height: 300px;
  overflow-y: auto;
  width: inherit;
  border: 1px solid #64CC9A;
  border-top: 0;
  margin-top: -2px;
  padding: 10px;
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

a.disabled {
  cursor: default;
  color: lightgray;
}

</style>
