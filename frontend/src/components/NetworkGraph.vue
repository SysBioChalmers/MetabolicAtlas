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
        <div id="searchResults" v-show="searchTerm.length > 1">
          <div v-if="searchResults.length > 0" v-for="r in searchResults" class="searchResultSection">
            <label class="title is-5" v-html="formatSearchResultLabel(r, searchTerm)"></label>
            <div>
              <span
                class="tag is-primary is-medium"
                @click="selectSearchResult(2, r.id)"
              >
                Closest interaction partners
              </span>
              <span
                class="tag is-primary is-medium"
                v-show="r.component_type==='enzyme'"
                @click="selectSearchResult(3, r.id)"
              >
                Catalysed reactions
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

import axios from 'axios';
import MetabolicNetwork from 'components/MetabolicNetwork';
import ClosestInteractionPartners from 'components/ClosestInteractionPartners';
import ConnectedMetabolites from 'components/ConnectedMetabolites';
import Metabolite from 'components/Metabolite';
import { chemicalFormula } from '../helpers/chemical-formatters';

export default {
  name: 'network-graph',
  components: {
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
          .catch((error) => {
            this.searchResults = [];
            console.log(error);
          });
      }, 500)();
    },
    selectSearchResult(tabIndex, reactionComponentId) {
      this.searchTerm = '';
      this.searchResults = [];
      this.goToTab(tabIndex, reactionComponentId, null);
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
