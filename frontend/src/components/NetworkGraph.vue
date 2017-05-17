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
          <input id="search" class="input" v-model="searchTerm"
            type="text" :placeholder="$t('searchPlaceholder')">
        </p>
        <div id="searchResults" v-show="searchTerm.length > 2">
          <div class="searchResultSection">
            <label class="title is-5">SULT1A3</label>
            <div>
              <span class="tag is-primary is-medium">Closest interaction partners</span>
              <span class="tag is-primary is-medium">Catalysed reactions</span>
            </div>
          </div>
          <div class="searchResultSection">
            <label class="title is-5">SULT1A5</label>
            <div>
              <span class="tag is-primary is-medium">Closest interaction partners</span>
              <span class="tag is-primary is-medium">Catalysed reactions</span>
              <span class="tag is-primary is-medium">Metabolites</span>
            </div>
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

import MetabolicNetwork from 'components/MetabolicNetwork';
import ClosestInteractionPartners from 'components/ClosestInteractionPartners';
import ConnectedMetabolites from 'components/ConnectedMetabolites';
import Reactome from 'components/Reactome';
import router from '../router';

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
      router.push({ query: { ...this.$route.query, tab: this.selectedTab } });
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
