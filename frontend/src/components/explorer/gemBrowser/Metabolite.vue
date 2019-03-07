<template>
  <div id="metabolite-page">
    <div v-if="errorMessage" class="columns">
      <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
        {{ errorMessage }}
      </div>
    </div>
    <div v-else>
      <div class="columns">
        <div class="column">
          <h3 class="title is-3">Metabolite {{ metabolite.name }}</h3>
        </div>
      </div>
      <div class="columns is-multiline metabolite-table">
        <div class="column is-10-widescreen is-9-desktop is-full-tablet">
          <table v-if="metabolite && Object.keys(metabolite).length != 0" class="table main-table is-fullwidth">
            <tr v-for="el in mainTableKey[model.database_name]">
              <td v-if="el.display" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
              <td v-else-if="el.name == 'id'" class="td-key has-background-primary has-text-white-bis">{{ model.short_name }} ID</td>
              <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
              <td v-if="metabolite[el.name] !== null">
                <span v-if="el.modifier" v-html="el.modifier(metabolite[el.name])">
                </span>
                <span v-else-if="el.name == 'compartment'">
                  <router-link :to="{ path: `/explore/gem-browser/${model.database_name}/compartment/${idfy(metabolite[el.name])}` }">{{ metabolite[el.name] }}</router-link>
                </span>
                <span v-else>
                  {{ metabolite[el.name] }}
                </span>
              </td>
              <td v-else> - </td>
            </tr>
          </table>
          <template v-if="hasExternalID">
            <br>
            <span class="subtitle">External IDs</span>
            <table v-if="metabolite && Object.keys(metabolite).length != 0" id="ed-table" class="table is-fullwidth">
              <tr v-for="el in externalIDTableKey[model.database_name]" v-if="metabolite[el.name] && metabolite[el.link]">
                <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
                <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
                <td>
                  <a :href="`http://${metabolite[el.link]}`" target="_blank">{{ metabolite[el.name] }}</a>
                </td>
              </tr>
            </table>
          </template>
        </div>
        <div class="column is-2-widescreen is-3-desktop is-full-tablet">
          <div class="box has-text-centered">
            <router-link class="button is-info is-fullwidth"
              :to="{path: `/explore/gem-browser/${model.database_name}/interaction/${this.mId}`}">
              {{ messages.interPartName }}
            </router-link>
          </div>
        </div>
      </div>
      <div class="columns">
        <reactome v-show="showReactome" id="metabolite-reactome" :model="model" :metaboliteID="metaboliteID"></reactome>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Reactome from 'components/explorer/gemBrowser/Reactome';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../../../helpers/chemical-formatters';
import { reformatTableKey, reformatStringToLink, addMassUnit, idfy } from '../../../helpers/utils';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'metabolite',
  components: {
    Reactome,
  },
  props: ['model'],
  data() {
    return {
      messages,
      mId: this.$route.params.id,
      metaboliteID: '',
      mainTableKey: {
        hmr2: [
          { name: 'name' },
          { name: 'alt_name', display: 'Alternate name' },
          { name: 'aliases', display: 'Synonyms' },
          { name: 'description', display: 'Description' },
          { name: 'formula', modifier: chemicalFormula },
          { name: 'charge' },
          { name: 'inchi' },
          { name: 'compartment' },
          { name: 'id' },
        ],
        yeast: [
          { name: 'name' },
          { name: 'alt_name', display: 'Alternate name' },
          { name: 'aliases', display: 'Synonyms' },
          { name: 'description', display: 'Description' },
          { name: 'formula', modifier: chemicalFormula },
          { name: 'charge' },
          { name: 'inchi' },
          { name: 'compartment' },
          { name: 'id' },
        ],
      },
      externalIDTableKey: {
        hmr2: [
          { name: 'hmdb_id', display: 'HMDB ID', link: 'hmdb_link' },
          { name: 'chebi_id', display: 'Chebi ID', link: 'chebi_link' },
          { name: 'mnxref_id', display: 'Mnxref ID', link: 'mnxref_link' },
        ],
        yeast: [
        ],
      },
      metabolite: {},
      errorMessage: '',
      activePanel: 'table',
      showReactome: false,
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.$route.path.includes('/metabolite/')) {
        if (this.mId !== this.$route.params.id) {
          this.setup();
        }
      }
    },
  },
  computed: {
    hasExternalID() {
      for (const item of this.externalIDTableKey[this.model.database_name]) {
        if (this.metabolite[item.name] && this.metabolite[item.link]) {
          return true;
        }
      }
      return false;
    },
  },
  methods: {
    setup() {
      this.mId = this.$route.params.id;
      if (this.mId) {
        this.load();
      }
    },
    load() {
      axios.get(`${this.model.database_name}/metabolite/${this.mId}/`)
      .then((response) => {
        this.metaboliteID = this.mId;
        this.metabolite = response.data;
        this.showReactome = true;
      })
      .catch(() => {
        this.errorMessage = messages.notFoundError;
        this.showReactome = false;
      });
    },
    reformatTableKey(k) { return reformatTableKey(k); },
    reformatLink(s, link) { return reformatStringToLink(s, link); },
    reformatMass(s) { return addMassUnit(s); },
    idfy,
  },
  beforeMount() {
    this.setup();
  },
  chemicalFormula,
  chemicalName,
  chemicalNameExternalLink,
};
</script>

<style lang="scss">

.metabolite-table, .model-table, .reaction-table, .subsystem-table {
  .main-table tr td.td-key, #ed-table tr td.td-key {
    width: 150px;
  }
}

</style>
