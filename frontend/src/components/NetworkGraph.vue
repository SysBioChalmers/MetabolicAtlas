<template>
  <div class="network-graph">
    <div class="columns">
      <div class="column is-3">
        <div class="tabs is-pulled-left is-toggle">
          <li class="is-active"><a><span>Human</span></a></li>
          <li><a><span>Yeast</span></a></li>
        </div>
      </div>
      <div class="column is-7">
        <p class="control">
          <input id="search" class="input"
            type="text" placeholder="Search by metabolite (uracil), gene (SULT1A3), or reaction (ATP[c] => cAMP[c] + PPi[c])">
        </p>
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
  </div>
</template>

<script>

import MetabolicNetwork from 'components/MetabolicNetwork';
import ClosestInteractionPartners from 'components/ClosestInteractionPartners';
import ConnectedMetabolites from 'components/ConnectedMetabolites';
import router from '../router';

export default {
  name: 'network-graph',
  components: {
    MetabolicNetwork,
    ClosestInteractionPartners,
    ConnectedMetabolites,
  },
  data() {
    return {
      selectedTab: 1,
      errorMessage: '',
      tabs: [
        'The whole metabolic network',
        'Zoom in on region',
        'Closest interaction partners',
        'Catalysed reactions',
        'Pathways',
        'Metabolites',
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
</style>
