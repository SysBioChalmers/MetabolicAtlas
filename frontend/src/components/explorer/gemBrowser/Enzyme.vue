<template>
  <div class="connected-metabolites">
    <div v-if="errorMessage" class="columns">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </div>
    <div v-show="!errorMessage">
      <div class="container columns">
        <div class="column">
          <h3 class="title is-3">
          Enzyme {{ enzyme.enzymeName }}
          </h3>
        </div>
      </div>
      <div class="columns">
        <div class="column">
          <div class="columns is-multiline">
            <div id="enzyme-details" class="reaction-table column is-10-widescreen is-9-desktop is-full-tablet">
              <table v-if="enzyme && Object.keys(enzyme).length != 0" class="table main-table is-fullwidth">
                <tr v-for="el in mainTableKey[model.database_name]">
                  <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
                  <td v-else-if="el.name == 'id'" class="td-key has-background-primary has-text-white-bis">{{ model.short_name }} ID</td>
                  <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                  <td v-if="enzyme[el.name]">
                    <span v-if="'modifier' in el" v-html="el.modifier(enzyme)">
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
                  <tr v-for="el in externalIDTableKey[model.database_name]" v-if="enzyme[el.name] && enzyme[el.link]">
                    <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
                    <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                    <td>
                      <a :href="`http://${enzyme[el.link]}`" target="_blank">{{ enzyme[el.name] }}</a>
                    </td>
                  </tr>
                </table>
              </template>
            </div>
            <div class="column is-2-widescreen is-3-desktop is-full-tablet">
              <div class="box has-text-centered">
                <div class="button is-info is-fullwidth" disabled>
                  <p>View on {{ messages.mapViewerName }}</p>
                </div>
                <br>
                <div class="button is-info is-fullwidth"
                  @click="viewInteractionPartners">
                  {{ messages.interPartName }}
                </div>
                <br>
                <template v-if="model.database_name === 'hmr2'">
                  <a class="button is-info is-fullwidth" title="View on Human Protein Atlas" target="_blank"
                    :href="`https://www.proteinatlas.org/${enzyme.id}`">
                    ProteinAtlas.org
                  </a>
                </template>
              </div>
            </div>
          </div>
          <div class="columns">
            <div class="column">
              <loader v-show="loading"></loader>
              <template v-show="reactions.length > 0">
                <h4 class="title is-4" v-show="!loading">Reactome</h4>
                <reaction-table v-show="!loading" :reactions="reactions" :showSubsystem="true" :model="model"></reaction-table>
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
import ReactionTable from 'components/explorer/gemBrowser/ReactionTable';
import Loader from 'components/Loader';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../../../helpers/chemical-formatters';
import { reformatTableKey } from '../../../helpers/utils';
import { default as visitLink } from '../../../helpers/visit-link';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'enzyme',
  components: {
    ReactionTable,
    Loader,
  },
  props: ['model'],
  data() {
    return {
      messages,
      loading: true,
      errorMessage: null,
      eId: '',
      enzyme: {},
      enzymeName: '',
      mainTableKey: {
        hmr2: [
          { name: 'enzymeName', display: 'Gene&nbsp;name' },
          { name: 'prot_name', display: 'Protein&nbsp;name' },
          { name: 'gene_synonyms', display: 'Synonyms' },
          { name: 'function' },
          { name: 'id' },
        ],
        yeast: [
          { name: 'enzymeName', display: 'Gene&nbsp;name' },
          { name: 'prot_name', display: 'Protein&nbsp;name' },
          { name: 'gene_synonyms', display: 'Synonyms' },
          { name: 'function' },
          { name: 'id' },
        ],
      },
      externalIDTableKey: {
        hmr2: [
          { name: 'id', display: 'Ensembl ID', link: 'name_link' },
          { name: 'uniprot_id', display: 'Uniprot ID', link: 'uniprot_link' },
          { name: 'ncbi_id', display: 'NCBI ID', link: 'ncbi_link' },
        ],
        yeast: [],
      },
      reactions: [],
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.$route.path.includes('/enzyme/')) {
        if (this.eId !== this.$route.params.id) {
          this.setup();
        }
      }
    },
  },
  computed: {
    filename() {
      return `ma_catalyzed_reaction_${this.enzymeName}`;
    },
    hasExternalID() {
      for (const item of this.externalIDTableKey[this.model.database_name]) {
        if (this.enzyme[item.name] && this.enzyme[item.link]) {
          return true;
        }
      }
      return false;
    },
  },
  methods: {
    setup() {
      this.eId = this.$route.params.id;
      if (this.eId) {
        this.load();
      }
    },
    reformatTableKey(k) { return reformatTableKey(k); },
    load() {
      this.loading = true;
      // const enzymeId = this.eid;
      axios.get(`${this.model.database_name}/enzyme/${this.eId}/connected_metabolites`)
        .then((response) => {
          this.loading = false;
          this.errorMessage = null;
          this.eId = response.data.enzyme.id;
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
              this.errorMessage = messages.notFoundError;
              break;
            default:
              this.errorMessage = messages.unknownError;
          }
        });
    },
    viewInteractionPartners() {
      this.$router.push(`/explore/gem-browser/${this.model.database_name}/interaction/${this.enzyme.id}`);
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
