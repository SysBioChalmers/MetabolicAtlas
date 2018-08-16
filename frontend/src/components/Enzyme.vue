<template>
  <div class="connected-metabolites">
    <div v-if="errorMessage" class="columns">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </div>
    <div v-show="!errorMessage">
      <div class="container columns">
        <div class="column is-5">
          <h3 class="title is-3">
          Enzyme | {{ enzymeName }}
          <span class="button is-info" title="View on Human Protein Atlas" v-if="model === 'hmr2'"
          @click="visitLink('https://www.proteinatlas.org/' + enzyme.id, true)">
            View on HPA
          </span>
          </h3>
        </div>
      </div>
      <div class="columns">
        <div class="column">
          <div class="columns">
            <div id="enzyme-details" class="reaction-table column is-10">
              <table v-if="enzyme && Object.keys(enzyme).length != 0" class="table main-table is-fullwidth">
                <tr v-for="el in mainTableKey[model]">
                  <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
                  <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                  <td v-if="enzyme[el.name]">
                    <span v-if="'modifier' in el" v-html=" el.modifier(enzyme)">
                    </span>
                    <span v-else>
                      {{ enzyme[el.name] }}
                    </span>
                  </td>
                  <td v-else> - </td>
                </tr>
              </table>
              <template v-if="hasExternalID">
                <br>
                <span class="subtitle">External IDs</span>
                <table v-if="enzyme && Object.keys(enzyme).length != 0" id="ed-table" class="table is-fullwidth">
                  <tr v-for="el in externalIDTableKey[model]" v-if="enzyme[el.name]">
                    <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
                    <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                    <td>
                      <span v-html="reformatLink(enzyme[el.name], enzyme[el.link])">
                      </span>
                    </td>
                  </tr>
                </table>
              </template>
            </div>
            <div class="column">
              <div class="box has-text-centered">
                <div class="button is-info">
                  <p><i class="fa fa-eye"></i> on Metabolic Viewer<p>
                </div>
                <br><br>
                <div class="button is-info"
                  @click="viewInteractionPartners">
                  View interaction partners
                </div>
              </div>
            </div>
          </div>
          <div class="columns">
            <div class="column">
              <loader v-show="loading"></loader>
              <template v-show="!loading && reactions.length > 0">
                <h3 class="title is-3">Reactome</h3>
                <reaction-table v-show="!loading" :reactions="reactions" :showSubsystem="true"></reaction-table>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ReactionTable from 'components/ReactionTable';
import Loader from 'components/Loader';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../helpers/chemical-formatters';
import { reformatTableKey, reformatStringToLink } from '../helpers/utils';
import { default as visitLink } from '../helpers/visit-link';

export default {
  name: 'enzyme',
  components: {
    ReactionTable,
    Loader,
  },
  props: ['model'],
  data() {
    return {
      loading: true,
      errorMessage: null,
      id: '',
      enzyme: {},
      enzymeName: '',
      mainTableKey: {
        hmr2: [
          { name: 'enzymeName', display: 'Gene&nbsp;Name' },
          { name: 'function' },
          { name: 'id', display: 'Model&nbsp;ID' },
        ],
      },
      externalIDTableKey: {
        hmr2: [
          { name: 'id', display: 'Ensembl ID', link: 'name_link' },
          { name: 'uniprot_id', display: 'Uniprot ID', link: 'uniprot_link' },
          { name: 'ncbi_id', display: 'NCBI ID', link: 'ncbi_link' },
        ],
      },
      reactions: [],
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  computed: {
    filename() {
      return `ma_catalyzed_reaction_${this.enzymeName}`;
    },
    hasExternalID() {
      for (const item of this.externalIDTableKey[this.model]) {
        if (this.enzyme[item.name]) {
          return true;
        }
      }
      return false;
    },
  },
  methods: {
    setup() {
      this.id = this.$route.params.id;
      this.load();
    },
    reformatTableKey(k) { return reformatTableKey(k); },
    reformatLink(s, link) { return reformatStringToLink(s, link); },
    load() {
      this.loading = true;
      const enzymeId = this.id;
      axios.get(`${this.model}/enzymes/${enzymeId}/connected_metabolites`)
        .then((response) => {
          this.loading = false;
          this.errorMessage = null;
          this.id = response.data.enzyme.id;
          this.enzymeName = response.data.enzyme.gene_name || response.data.enzyme.id;
          this.enzyme = response.data.enzyme;
          this.enzyme.enzymeName = this.enzymeName;
          this.reactions = response.data.reactions;
        })
        .catch((error) => {
          this.loading = false;
          this.reactions = [];
          switch (error.response.status) {
            case 404:
              this.errorMessage = this.$t('notFoundError');
              break;
            default:
              this.errorMessage = this.$t('unknownError');
          }
        });
    },
    viewInteractionPartners() {
      this.$router.push(`/GemsExplorer/${this.model}/interaction/${this.enzyme.id}`);
    },
    chemicalFormula,
    chemicalName,
    chemicalNameExternalLink,
    visitLink,
  },
  beforeMount() {
    this.setup();
  },
};

</script>

<style lang="scss">

h1, h2 {
  font-weight: normal;
}

</style>
