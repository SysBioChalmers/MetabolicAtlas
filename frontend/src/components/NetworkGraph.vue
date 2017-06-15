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
      :fastSearch=true
      ><global-search>
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
   <closest-interaction-partners v-if="selectedTab===3" 
    @updateSelTab="goToTab"></closest-interaction-partners>
   <connected-metabolites v-if="selectedTab===4" 
    @updateSelTab="goToTab"></connected-metabolites>
   <metabolite v-if="selectedTab===5"></metabolite>
  </div>
</template>

<script>

import GlobalSearch from 'components/GlobalSearch';
import MetabolicNetwork from 'components/MetabolicNetwork';
import ClosestInteractionPartners from 'components/ClosestInteractionPartners';
import ConnectedMetabolites from 'components/ConnectedMetabolites';
import Reactome from 'components/Reactome';

export default {
  name: 'network-graph',
  components: {
    GlobalSearch,
    MetabolicNetwork,
    ClosestInteractionPartners,
    ConnectedMetabolites,
    Metabolite,
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
    goToTab(tabIndex, reactionComponentId, metaboliteRcId) {
      this.selectedTab = tabIndex + 1;
      this.$router.push({ query: { ...this.$route.query, tab: this.selectedTab } });
    },
      const fullQuery = {
        ...this.$route.query,
        tab: this.selectedTab,
      };
      if (reactionComponentId) {
        fullQuery.reaction_component_id = reactionComponentId;
      }
      if (reactionComponentId) {
        fullQuery.metabolite_rcid = metaboliteRcId;
      }
      this.$router.push({
        query: fullQuery,
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
</style>
