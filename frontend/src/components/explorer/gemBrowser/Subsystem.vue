<template>
  <div class="section extended-section">
    <div class="container is-fullhd">
      <div v-if="modelErrorMessage" class="columns is-centered">
        <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
          {{ modelErrorMessage }}
        </div>
      </div>
      <div v-if="componentNotFound" class="columns is-centered">
        <notFound :type="type" :component-id="sName"></notFound>
      </div>
      <div v-else>
        <div class="columns">
          <div class="column">
            <h3 class="title is-3"><span class="is-capitalized">{{ type }}</span> {{ info.name }}</h3>
          </div>
        </div>
        <loader v-if="showLoaderMessage" :message="showLoaderMessage" class="columns" />
        <div v-else class="columns is-multiline is-variable is-8">
          <div class="subsystem-table column is-10-widescreen is-9-desktop is-full-tablet">
            <div class="table-container">
              <table v-if="info && Object.keys(info).length !== 0" class="table main-table is-fullwidth">
                <tr v-for="el in mainTableKey" :key="el.name" class="m-row">
                  <template v-if="info[el.name]">
                    <td v-if="el.display" class="td-key has-background-primary has-text-white-bis">{{ el.display }}</td>
                    <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatKey(el.name) }}</td>
                    <td v-if="info[el.name]">
                      <span v-if="el.modifier" v-html="el.modifier(info[el.name])"></span>
                      <span v-else>{{ info[el.name] }}</span>
                    </td>
                    <td v-else> - </td>
                  </template>
                </tr>
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis">Compartments</td>
                  <td>
                    <div class="tags">
                      <template v-for="c in info['compartments']">
                        <span :key="c.id" class="tag">
                          <!-- eslint-disable-next-line max-len -->
                          <router-link :to="{ name: 'compartment', params: { model: model.short_name, id: c.id } }">{{ c.name }}</router-link>
                        </span>
                      </template>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis">Metabolites</td>
                  <td>
                    <div v-html="metabolitesListHtml"></div>
                    <div v-if="!showFullMetabolite && metabolites.length > displayedMetabolite">
                      <br>
                      <button class="is-small button" @click="showFullMetabolite=true">
                        ... and {{ metabolites.length - displayedMetabolite }} more
                      </button>
                      <span v-show="metabolites.length === limitMetabolite"
                            class="tag is-medium is-warning is-pulled-right">
                        The number of metabolites displayed is limited to {{ limitMetabolite }}.
                      </span>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis">Genes</td>
                  <td>
                    <div v-html="genesListHtml"></div>
                    <div v-if="!showFullGene && genes.length > displayedGene">
                      <br>
                      <button class="is-small button" @click="showFullGene=true">
                        ... and {{ genes.length - displayedGene }} more
                      </button>
                      <span v-show="genes.length === limitGene" class="tag is-medium is-warning is-pulled-right">
                        The number of genes displayed is limited to {{ limitGene }}.
                      </span>
                    </div>
                  </td>
                </tr>
              </table>
            </div>
            <ExtIdTable :type="type" :external-dbs="info.externalDbs"></ExtIdTable>
          </div>
          <div class="column is-2-widescreen is-3-desktop is-half-tablet has-text-centered">
            <maps-available :id="sName" :type="type" :element-i-d="''"></maps-available>
            <gem-contact :id="sName" :type="type" />
          </div>
        </div>
        <reaction-table v-if="model" :source-name="sName" :type="type" />
      </div>
    </div>
  </div>
</template>


<script>

import { mapGetters, mapState } from 'vuex';
import NotFound from '@/components/NotFound';
import Loader from '@/components/Loader';
import MapsAvailable from '@/components/explorer/gemBrowser/MapsAvailable';
import ExtIdTable from '@/components/explorer/gemBrowser/ExtIdTable';
import ReactionTable from '@/components/explorer/gemBrowser/ReactionTable';
import GemContact from '@/components/shared/GemContact';
import { buildCustomLink, reformatTableKey } from '@/helpers/utils';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'Subsystem',
  components: {
    NotFound,
    Loader,
    MapsAvailable,
    ReactionTable,
    ExtIdTable,
    GemContact,
  },
  data() {
    return {
      sName: this.$route.params.id,
      type: 'subsystem',
      modelErrorMessage: '',
      mainTableKey: [
        { name: 'name', display: 'Name' },
      ],
      showFullMetabolite: false,
      showFullGene: false,
      displayedMetabolite: 40,
      displayedGene: 40,
      componentNotFound: false,
      showLoaderMessage: '',
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
    ...mapGetters({
      info: 'subsystems/info',
      metabolites: 'subsystems/metabolites',
      genes: 'subsystems/genes',
      limitMetabolite: 'subsystems/limitMetabolite',
      limitGene: 'subsystems/limitGene',
    }),
    metabolitesListHtml() {
      const l = ['<span class="tags">'];
      const metsSorted = [...this.metabolites].sort((a, b) => (a.name < b.name ? -1 : 1));
      for (let i = 0; i < metsSorted.length; i += 1) {
        const m = metsSorted[i];
        if ((!this.showFullMetabolite && i === this.displayedMetabolite)
          || i === this.limitMetabolite) {
          break;
        }
        const customLink = buildCustomLink({ model: this.model.short_name, type: 'metabolite', id: m.id, title: m.name || m.id });
        l.push(
          `<span id="${m.id}" class="tag">${customLink}</span>`
        );
      }
      l.push('</span>');
      return l.join('');
    },
    genesListHtml() {
      const l = ['<span class="tags">'];
      const genesSorted = [...this.genes].sort((a, b) => (a.name < b.name ? -1 : 1));
      for (let i = 0; i < genesSorted.length; i += 1) {
        const e = genesSorted[i];
        if ((!this.showFullGene && i === this.displayedGene)
          || i === this.limitGene) {
          break;
        }
        const customLink = buildCustomLink({ model: this.model.short_name, type: 'gene', id: e.id, title: e.name || e.id });
        l.push(`<span id="${e.id}" class="tag">${customLink}</span>`);
      }
      l.push('</span>');
      return l.join('');
    },
  },
  watch: {
    '$route.params': 'setup',
  },
  async created() {
    if (!this.model || this.model.short_name !== this.$route.params.model) {
      const modelSelectionSuccessful = await this.$store.dispatch('models/selectModel', this.$route.params.model);
      if (!modelSelectionSuccessful) {
        this.modelErrorMessage = `Error: ${messages.modelNotFound}`;
      }
    }
    this.setup();
  },
  methods: {
    async setup() {
      this.sName = this.$route.params.id;
      this.showLoaderMessage = 'Loading subsystem data';
      try {
        const payload = { model: this.model, id: this.sName };
        await this.$store.dispatch('subsystems/getSubsystemSummary', payload);
        this.componentNotFound = false;
        this.showLoaderMessage = '';
      } catch {
        this.componentNotFound = true;
        document.getElementById('search').focus();
      }
    },
    reformatKey(k) { return reformatTableKey(k); },
  },
};
</script>

<style lang="scss"></style>
