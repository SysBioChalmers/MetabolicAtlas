<template>
  <div class="network-graph">
    <div class="columns">
      <div class="column is-3">
        <div class="tabs is-pulled-left is-toggle">
          <li class="is-active"><a><span>{{ $t('human') }}</span></a></li>
          <li v-if="false"><a><span>{{ $t('yeast') }}</span></a></li>
        </div>
      </div>
      <global-search
      :quickSearch=true
      ></global-search>
      <div class="column">
        <div class="is-pulled-right">
          <a @click="viewRelaseNotes">Release 1.0</a>
        </div>
      </div>
    </div>
    <br>
    <div class="tabs is-boxed is-centered">
      <ul>
        <li
         v-for="(tab, index) in tabs"
         :class="[{ 'is-active': isActive(index) }, { 'is-disabled': tab.isDisabled }]"
         :disabled="tab.isDisabled"
         @click="goToTab(tab.type, componentID)"
        >
         <a :class="{ 'disabled': tab.isDisabled }"><span>{{ tab.title }}</span></a>
        </li>
      </ul>
    </div>
    <div v-if="errorMessage">
      {{ errorMessage }}
    </div>
    <div v-else>
      <metabolic-network v-show="selectedTab===1"></metabolic-network>
      <closest-interaction-partners v-if="selectedTab===2"></closest-interaction-partners>
      <enzyme v-if="selectedTab===3"></enzyme>
      <metabolite v-if="selectedTab===4"></metabolite>
      <reaction v-if="selectedTab===5"></reaction>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import GlobalSearch from 'components/GlobalSearch';
import MetabolicNetwork from 'components/MetabolicNetwork';
import ClosestInteractionPartners from 'components/ClosestInteractionPartners';
import Enzyme from 'components/Enzyme';
import Metabolite from 'components/Metabolite';
import Reaction from 'components/Reaction';
import router from '../router';
import { default as EventBus } from '../event-bus';

export default {
  name: 'network-graph',
  components: {
    MetabolicNetwork,
    ClosestInteractionPartners,
    Enzyme,
    Metabolite,
    Reaction,
    GlobalSearch,
  },
  data() {
    return {
      selectedTab: 1,
      searchTerm: '',
      searchResults: [],
      errorMessage: '',
      componentID: '',
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  created() {
    console.log('network_graph_crated');
    // init the global events
    EventBus.$on('resetView', () => {
      this.levelSelected = 'subsystem';
      EventBus.$emit('showSVGmap', 'wholemap', null, []);
    });
    EventBus.$on('updateSelTab', (type, id) => {
      console.log(`on updateSelTab ${type} ${id}`);
      this.goToTab(type, id);
    });
  },
  beforeMount() {
    this.setup();
  },
  computed: {
    tabs() {
      let disabledTab2 = true;
      let disabledTab3 = true;
      let disabledTab4 = true;
      let disabledTab5 = true;
      if (this.componentID) {
        disabledTab2 = this.componentID[0] === 'R';
        disabledTab3 = this.componentID[0] !== 'E';
        disabledTab4 = this.componentID[0] !== 'M';
        disabledTab5 = this.componentID[0] !== 'R';
      }

      return [
        { title: this.$t('tab1title'), type: 'map', isDisabled: false },
        { title: this.$t('tab2title'), type: 'interaction', isDisabled: disabledTab2 },
        { title: this.$t('tab3title'), type: 'enzyme', isDisabled: disabledTab3 },
        { title: this.$t('tab4title'), type: 'metabolite', isDisabled: disabledTab4 },
        { title: this.$t('tab5title'), type: 'reaction', isDisabled: disabledTab5 },
      ];
    },
  },
  methods: {
    setup() {
      this.selectedTab = parseInt(this.$route.query.tab, 10) || 1;
      this.componentID = this.$route.query.id;
    },
    isActive(tabIndex) {
      return tabIndex + 1 === this.selectedTab;
    },
    goToTab(type, componentID) {
      let tabIndex = 0;
      // let queryName = 'id';
      if (type) {
        switch (type) {
          case 'metabolite':
            tabIndex = 3;
            break;
          case 'enzyme':
            tabIndex = 2;
            break;
          case 'reaction':
            tabIndex = 4;
            break;
          case 'interaction':
            tabIndex = 1;
            break;
          case 'map':
            tabIndex = 0;
            break;
          default:
            tabIndex = 0;
        }
      }

      this.componentID = componentID;
      if (this.tabs[tabIndex].isDisabled) {
        return;
      }

      if ([1, 2, 3, 4].includes(this.tabIndex) && !componentID) {
        this.errorMessage = this.$t('noIDProvided');
      } else {
        this.errorMessage = '';
      }

      this.selectedTab = tabIndex + 1;

      const fullQuery = {
        ...this.$route.query,
        tab: this.selectedTab,
      };
      if (tabIndex === 0) {
        delete fullQuery.id;
      } else if (componentID) {
        // remove the current key if other than 'id'
        fullQuery.id = componentID;
      }

      // console.log(fullQuery);

      this.$router.push({
        query: fullQuery,
      });

      if (tabIndex === 0) {
        console.log('on tab 0 resetview ?');
        // EventBus.$emit('resetView');
      }
    },
    search() {
      if (this.searchTerm.length < 2) {
        return;
      }
      const searchTerm = this.searchTerm;
      this._.debounce(() => {
        axios.get(`search/${searchTerm}`)
          .then((response) => {
            this.searchResults = response.data;
          })
          .catch(() => {
            this.searchResults = [];
          });
      }, 500)();
    },
    selectSearchResult(tabIndex, componentID) {
      this.searchTerm = '';
      this.searchResults = [];
      this.goToTab(tabIndex, componentID);
    },
    viewRelaseNotes() {
      router.push({
        path: '/About#releaseNotes',
        query: {},
      });
    },
  },
};

</script>

<style lang="scss">

a.disabled {
  cursor: default;
  color: lightgray;
}

</style>
