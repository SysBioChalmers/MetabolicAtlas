<template>
  <div>
    <div class="container columns">
      <div class="column is-offset-3">
        <global-search
        :quickSearch=false
        :searchTerm=searchTerm
        @updateResults="updateResults">
        </global-search>
      </div>
    </div>
    <div>
      <div class="tabs is-boxed is-fullwidth">
        <ul>
          <li :disabled="resultsCount[tab] === 0" 
          :class="[{'is-active': showTab(tab) && resultsCount[tab] !== 0 }, { 'is-disabled': resultsCount[tab] === 0 }]" 
          v-for="tab in tabs" @click="resultsCount[tab] !== 0 ? showTabType=tab : ''">
            <a>{{ tab | capitalize }} ({{ resultsCount[tab] }})</a>
          </li>
        </ul>
      </div>
      <div v-show="showTab('metabolite') && resultsCount['metabolite'] !== 0">
        Metabolite results
        <div class="columns">
          <div class="column">
            <table class="table main">
              <thead>
                <tr>
                  <th>Organism</th>
                  <th>Model</th>
                  <th>Pathway</th>
                  <th>Compartment</th>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Formula</th>
                  <th>HMDB ID</th>
                  <th>Link</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in searchResultsOrdered" v-if="resultsCount['metabolite'] !== 0 && item.component_type === 'metabolite'">
                  <td>{{ item.organism | capitalize }}</td>
                  <td>the model</td>
                  <td>the pathway</td>
                  <td>{{ item.compartment | capitalize }}</td>
                  <td>{{ item.id.slice(2) }}</td>
                  <td>{{ item.short_name }}</td>
                  <td v-html="formulaFormater(item.formula)"></td>
                  <td>{{ item.metabolite ? item.metabolite.hmdb : '' }}</td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div v-show="showTab('enzyme') && resultsCount['enzyme'] !== 0">
        Enzyme results
        <div class="columns">
          <div class="column">
            <table class="table main">
              <thead>
                <tr>
                  <th>Organism</th>
                  <th>Model</th>
                  <th>Pathway</th>
                  <th>Compartment</th>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Formula</th>
                  <th>Uniprot ID</th>
                  <th>Link</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in searchResultsOrdered" v-if="resultsCount['enzyme'] !== 0 && item.component_type === 'enzyme'">
                  <td>{{ item.organism | capitalize }}</td>
                  <td>the model</td>
                  <td>the pathway</td>
                  <td>{{ item.compartment | capitalize }}</td>
                  <td>{{ item.id.slice(2) }}</td>
                  <td>{{ item.short_name }}</td>
                  <td v-html="formulaFormater(item.formula)"></td>
                  <td>{{ item.enzyme ? item.enzyme.uniprot_acc : '' }}</td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div v-show="showTab('reaction') && resultsCount['reaction'] !== 0">
        Reaction results
      </div>
      <div v-show="showTab('pathway') && resultsCount['pathway'] !== 0">
        Pathway results
      </div>
      <div v-show="showTab('compartment') && resultsCount['compartment'] !== 0">
        Compartement results
      </div>
      <div v-show="!showTabType">
        <div v-if="searchResults.length === 0" class="column is-8 is-offset-2 has-text-centered">
          {{ $t('searchNoResult') }}
        </div>
      </div>
    </div>
    <br>
    <hr>
    <br>
    <div>
      <div>
        <div v-if="searchResults.length === 0" class="columns">
          <div class="column is-8 is-offset-2 has-text-centered">
            {{ $t('searchNoResult') }}
          </div>
        </div>
        <div v-else>
          Results: {{ searchResults.length }}
          <section class="res-section metabolite-div columns is-multiline" v-for="item in searchResultsOrdered" v-if="item.component_type === 'metabolite'">
            <div class="res-title column is-12">{{ item.component_type | capitalize }}</div>
            <div class="res-label column is-1">ID/name:</div>
            <div class="column is-8">{{ item.id.slice(2) }} - {{ item.short_name }} - <span v-html="formulaFormater(item.formula)"></span></div>
            <div class="res-label column is-1">HMDB ACC:</div>
            <div class="column is-2"> {{ item.metabolite ? item.metabolite.hmdb : '' }}</div>
            <div class="res-label column is-1">Model:</div>
            <div class="column is-5">'the model' ({{ item.organism | capitalize }})</div>
            <div class="res-label column is-1">Localization:</div>
            <div class="column is-5"> {{ item.compartment | capitalize }} | 'the pathway name'</div>
            <div class="res-label column is-1">Description:</div>
            <div class="column is-11"> 'the description' </div>
          </section>
          <section class="res-section enzyme-div columns is-multiline" v-else-if="item.component_type === 'enzyme'">
            <div class="res-title column is-12">{{ item.component_type | capitalize }}</div>
            <div class="res-label column is-1">ID/name:</div>
            <div class="column is-8">{{ item.id.slice(2) }} - {{ item.short_name }}</div>
            <div class="res-label column is-1">UNIPROT ACC:</div>
            <div class="column is-2"> {{ item.enzyme ? item.enzyme.uniprot_acc : '' }}</div>
            <div class="res-label column is-1">Model:</div>
            <div class="column is-5">'the model' ({{ item.organism | capitalize }})</div>
            <div class="res-label column is-1">Localization:</div>
            <div class="column is-5"> {{ item.compartment | capitalize }} | 'the pathway name'</div>
            <div class="res-label column is-1">Description:</div>
            <div class="column is-11"> 'the description' </div>
          </section>
          <section class="res-section reaction-div columns is-multiline">
            <div class="res-title column is-12">Reaction</div>
              <div class="res-label column is-1">ID/name:</div>
              <div class="column is-8">R_HMR_0001 - 'reaction name'</div>
              <div class="res-label column is-1">ACC:</div>
              <div class="column is-2"> SBO:0000176 - EC:3.1.1.23</div>
              <div class="res-label column is-1">Model:</div>
              <div class="column is-5">'the model' (Human)</div>
              <div class="res-label column is-1">Localization:</div>
              <div class="column is-5"> 'the compartment' | 'the pathway name (subsytem)'</div>
              <div class="res-label column is-1">Equation:</div>
              <div class="column is-11">1-acylglycerol-chylomicron pool[s] => 1-acylglycerol-chylomicron pool[c]</div>
              <div class="res-label column is-1">Description:</div>
              <div class="column is-11">'the description'</div>
          </section>
          <section class="res-section pathway-div columns is-multiline">
            <div class="res-title column is-12">Pathway</div>
              <div class="res-label column is-1">ID/name:</div>
              <div class="column is-8">P-00125 - 'pathway name'</div>
              <div class="res-label column is-1">KEGG ACC:</div>
              <div class="column is-2">XXXXX</div>
              <div class="res-label column is-1">Model:</div>
              <div class="column is-5">'the model' (Human)</div>
              <div class="res-label column is-1">Localization:</div>
              <div class="column is-5"> 'the compartment'</div>
              <div class="res-label column is-1">Description:</div>
              <div class="column is-11">'the description'</div>
          </section>
          <section class="res-section compartment-div columns is-multiline">
            <div class="res-title column is-12">Compartment</div>
              <div class="res-label column is-1">ID/name:</div>
              <div class="column is-8">R_HMR_0001 - 'pathway name'</div>
              <div class="res-label column is-1">ACC:</div>
              <div class="column is-2">XXXXX</div>
              <div class="res-label column is-1">Model:</div>
              <div class="column is-11">'the model' (Human)</div>
              <div class="res-label column is-1">Description:</div>
              <div class="column is-11">'the description'</div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import GlobalSearch from 'components/GlobalSearch';
import { default as compare } from '../helpers/compare';
import { chemicalFormula } from '../helpers/chemical-formatters';

export default {
  name: 'search-table',
  components: {
    GlobalSearch,
  },
  data() {
    return {
      tabs: [
        'metabolite',
        'enzyme',
        'reaction',
        'pathway',
        'compartment',
      ],
      resultsCount: {
        metabolite: 0,
        enzyme: 0,
        reaction: 0,
        pathway: 0,
        compartment: 0,
      },
      searchTerm: 'metabolite',
      searchResults: [],
      showTabType: '',
    };
  },
  computed: {
    searchResultsOrdered() {
      let res = this.searchResults;
      res = res.sort(compare('component_type', 'asc'));
      return res;
    },
  },
  filters: {
    capitalize(value) {
      if (!value) {
        return '';
      }
      return value.charAt(0).toUpperCase() + value.slice(1);
    },
  },
  methods: {
    formulaFormater(s) {
      return chemicalFormula(s);
    },
    updateResults(term, val) {
      this.searchTerm = term;
      this.searchResults = val;

      // count types
      console.log('====');
      console.log(this.searchResults);
      for (const key of Object.keys(this.resultsCount)) {
        this.resultsCount[key] = 0;
      }
      for (const el of this.searchResults) {
        if (el.component_type in this.resultsCount) {
          this.resultsCount[el.component_type] += 1;
        } else {
          this.resultsCount.metabolite += 1;
        }
      }
      // set up the active tab
      for (const key of Object.keys(this.resultsCount)) {
        if (this.resultsCount[key] !== 0) {
          this.showTabType = key;
          return;
        }
      }
      this.showTabType = '';
    },
    showTab(elementType) {
      return this.showTabType === elementType;
    },
  },
  beforeMount() {
    this.searchTerm = this.$route.query.term;
  },
  mounted() {
    if (this.searchTerm) {
      // trigger the search in child component
      this.$children[0].search(this.searchTerm);
    }
  },
  chemicalFormula,
};

</script>

<style lang="scss">

.red {
  color: #ff1a1a;
}

.green {
  color: #33cc33;
}

table.main

table td.lab {
  font-weight: 600;
  background: lightgray;
  width: 150px;
  border: 1px solid gray;
}

.tabs li.is-disabled {
  cursor: not-allowed;
  color: gray;
  opacity: 0.75;

  a {
    cursor: not-allowed;
  }
}


.res-section {

  display: table;
  border-collapse:collapse;

  div {
    border: 1px solid black;
    display:table-row;
  }

  div.res-title {
    font-weight: 600;
    font-size: 16px;
    padding: 0 0.75rem;
    background: rgba(0, 0, 0,0.1 );
  }

  div.res-label {
    text-decoration: underline;
  }
}

.metabolite-div {
  background: rgba(102, 255, 102, 0.1);
}

.enzyme-div {
  background: rgba(255, 0, 0, 0.1);
}

.reaction-div {
  background: rgba(255, 153, 0, 0.1);
}

.pathway-div {
  background: rgba(128, 0, 128, 0.1);
}

.compartment-div {
  background: rgba(0, 0, 255, 0.1);
}

</style>
