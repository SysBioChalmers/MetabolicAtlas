<template>
  <div class="network-graph">
    <div class="columns">
      <div class="column is-3">
        <div class="tabs is-pulled-left is-toggle">
          <li class="is-active"><a><span>{{ $t('human') }}</span></a></li>
          <li><a><span>{{ $t('yeast') }}</span></a></li>
        </div>
      </div>
      <div class="column is-7">
        <p class="control">
          <input
            id="search"
            class="input"
            v-model="searchTerm"
            @input="search"
            type="text"
            :placeholder="$t('searchPlaceholder')">
        </p>
        <div id="searchResults" v-show="searchTerm.length > 2 && searchResults.length > 0">
          <div v-for="r in searchResults" class="searchResultSection">
            <label class="title is-5">{{ r.short_name || r.long_name }}</label>
            <div>
              <span
                class="tag is-primary is-medium"
                @click="selectSearchResult(3, r.id)"
              >
                Closest interaction partners
              </span>
              <span
                class="tag is-primary is-medium"
                v-show="r.component_type=='enzyme'"
                @click="selectSearchResult(4, r.id)"
              >
                Catalysed reactions
              </span>
            </div>
            <hr>
          </div>
        </div>
      </div>
    </div>
    <br>
    <div class="tabs is-boxed">
     <ul>
       <li
         v-for="(tab, index) in tabs"
         :class="[{ 'is-active': isActive(index) }, '']"
         @click="goToTab(index)"
       >
        <a><span>{{ tab }}</span></a>
       </li>
     </ul>
   </div>
   <metabolic-network v-if="selectedTab===1"></metabolic-network>
   <closest-interaction-partners v-if="selectedTab===3"></closest-interaction-partners>
   <connected-metabolites v-if="selectedTab===4"></connected-metabolites>
   <reactome v-if="selectedTab===5"></reactome>
  </div>
</template>

<script>

import axios from 'axios';
import MetabolicNetwork from 'components/MetabolicNetwork';
import ClosestInteractionPartners from 'components/ClosestInteractionPartners';
import ConnectedMetabolites from 'components/ConnectedMetabolites';
import Reactome from 'components/Reactome';

export default {
  name: 'network-graph',
  components: {
    MetabolicNetwork,
    ClosestInteractionPartners,
    ConnectedMetabolites,
    Reactome,
  },
  data() {
    return {
      selectedTab: 1,
      searchTerm: '',
      searchResults: [],
      errorMessage: '',
      tabs: [
        this.$t('tab1title'),
        this.$t('tab2title'),
        this.$t('tab3title'),
        this.$t('tab4title'),
        this.$t('tab5title'),
        this.$t('tab6title'),
      ],
    };
  },
  beforeMount() {
    this.selectedTab = parseInt(this.$route.query.tab, 10) || 1;
  },
  methods: {
    isActive(tabIndex) {
      return tabIndex + 1 === this.selectedTab;
    },
    goToTab(tabIndex) {
      this.selectedTab = tabIndex + 1;
      this.$router.push({ query: { ...this.$route.query, tab: this.selectedTab } });
    },
    search() {
      if (this.searchTerm.length < 3) {
        return;
      }
      this._.debounce(() => {
        axios.get(`search/${this.searchTerm}`)
          .then((response) => {
            this.searchResults = response.data;
          })
          .catch((error) => {
            this.searchResults = [];
            console.log(error);
          });
      }, 500)();
    },
    selectSearchResult(tab, reactionComponentId) {
      this.searchTerm = '';
      this.searchResults = [];
      this.selectedTab = tab;
      this.$router.push({
        query: {
          ...this.$route.query,
          reaction_component_id: reactionComponentId,
          tab: this.selectedTab,
        },
      });
    },
  },
};
</script>

<style lang="scss">

#search {
  height: 38px;
}

#searchResults {
  max-height: 300px;
  overflow-y: auto;
  width: 100%;
  border: 1px solid #64CC9A;
  border-top: 0;
  margin-top: -2px;
  padding: 10px;

  .searchResultSection {
    margin-bottom: 10px;

    label {
      font-style: italic;
    }

    span {
      cursor: pointer;
    }
  }
}

</style>
