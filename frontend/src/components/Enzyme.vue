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
                  <td v-if="'display' in el" class="td-key">{{ el.display }}</td>
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
              <div v-show="!loading">
                <div v-show="reactions.length > 0">
                  <loader v-show="loading"></loader>
                  <reaction-table v-show="!loading" :reactions="reactions" :showSubsystem="true"></reaction-table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import ReactionTable from 'components/ReactionTable';
import Loader from 'components/Loader';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../helpers/chemical-formatters';
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
          { name: 'enzymeName', display: 'Gene Name' },
          { name: 'function', display: 'Function' },
          { name: 'id', display: 'Model ID' },
          { name: 'uniprot', display: 'Uniprot ID', modifier: this.reformatUniprotLink },
          { name: 'ncbi', display: 'NCBI ID', modifier: this.reformatNCBILink },
          { name: 'id', display: 'Ensembl ID', modifier: this.reformatEnsemblLink },
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
  },
  methods: {
    setup() {
      this.id = this.$route.params.id;
      this.load();
    },
    reformatList(l) {
      let output = '';
      if (l.length) {
        output = l.join('; ');
      } else {
        output = '-';
      }
      return output;
    },
    reformatUniprotLink(enzyme) {
      return `<a href="${enzyme.uniprot_link}" target="_blank">${enzyme.uniprot}</a>`;
    },
    reformatNCBILink(enzyme) {
      return `<a href="${enzyme.ncbi_link}" target="_blank">${enzyme.ncbi}</a>`;
    },
    reformatEnsemblLink(enzyme) {
      return `<a href="${enzyme.ensembl_link}" target="_blank">${enzyme.id}</a>`;
    },
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
    scrollTo(id) {
      const container = $('body, html');
      container.scrollTop(
        $(`#${id}`).offset().top - (container.offset().top + container.scrollTop())
      );
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
