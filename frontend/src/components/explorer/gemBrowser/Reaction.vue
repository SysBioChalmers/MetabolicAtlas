<template>
  <div class="section extended-section">
    <div class="container is-fullhd">
      <div v-if="modelErrorMessage" class="columns is-centered">
        <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
          {{ modelErrorMessage }}
        </div>
      </div>
      <div v-if="componentNotFound" class="columns is-centered">
        <notFound :type="type" :component-id="rId"></notFound>
      </div>
      <div v-else>
        <div class="columns">
          <div class="column">
            <h3 class="title is-size-3"><span class="is-capitalized">{{ type }}</span> {{ reaction.id }}</h3>
          </div>
        </div>
        <loader v-if="showLoaderMessage" :message="showLoaderMessage" class="columns" />
        <div v-else class="columns is-multiline is-variable is-8">
          <div class="reaction-table column is-10-widescreen is-9-desktop is-full-tablet">
            <div class="table-container">
              <table v-if="reaction && Object.keys(reaction).length !== 0" class="table main-table is-fullwidth">
                <tr v-for="el in mainTableKey" :key="el.name">
                  <td v-if="'display' in el"
                      class="td-key has-background-primary has-text-white-bis"
                      v-html="el.display"></td>
                  <td v-else-if="el.name === 'id'"
                      class="td-key has-background-primary has-text-white-bis">
                    {{ model.short_name }} ID</td>
                  <td v-else class="td-key has-background-primary has-text-white-bis">
                    {{ reformatTableKey(el.name) }}
                  </td>
                  <td v-if="reaction[el.name]">
                    <template v-if="'modifier' in el"><span v-html="el.modifier()"></span></template>
                    <template v-else-if="el.name === 'subsystems'">
                      <template v-for="(v, i) in reaction[el.name]">
                        <template v-if="i !== 0">; </template>
                        <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key max-len -->
                        <router-link :to="{ name: 'subsystem', params: { model: model.short_name, id: v.id } }"> {{ v.name }}</router-link>
                      </template>
                    </template>
                    <template v-else-if="el.name === 'compartments'">
                      <div class="tags">
                        <template v-for="c in reaction[el.name]">
                          <span :key="c.id" class="tag">
                            <!-- eslint-disable-next-line max-len -->
                            <router-link :to="{ name: 'compartment', params: { model: model.short_name, id: c.id } }">{{ c.name }}</router-link>
                          </span>
                        </template>
                      </div>
                    </template>
                    <template v-else-if="el.name === 'ec'">
                      <!-- eslint-disable-next-line max-len -->
                      <router-link v-for="eccode in reaction[el.name].split('; ')" :key="eccode" :to="{ name: 'search', query: { term: eccode }}">
                        {{ eccode }}
                      </router-link>
                    </template>
                    <template v-else>{{ reaction[el.name] }}</template>
                  </td>
                  <td v-else-if="'modifier' in el"><span v-html="el.modifier()"></span></td>
                  <td v-else> - </td>
                </tr>
                <tr v-if="relatedReactions.length !== 0">
                  <td class="td-key has-background-primary has-text-white-bis">Related reaction(s)</td>
                  <td>
                    <span v-for="rr in relatedReactions" :key="rr.id">
                      <router-link :to="{ name: 'reaction', params: { model: model.short_name, id: rr.id } }">
                        {{ rr.id }}
                      </router-link>:&nbsp;
                      <span v-html="reformatChemicalReactionHTML(rr, true, model.short_name)"></span>:
                      (<span v-html="equationSign(rr.reversible)">
                      </span>)
                    </span>
                  </td>
                </tr>
              </table>
            </div>
            <ExtIdTable :type="type" :external-dbs="reaction.externalDbs"></ExtIdTable>
            <br>
            <references :reference-list="referenceList" />
          </div>
          <div class="column is-2-widescreen is-3-desktop is-half-tablet has-text-centered">
            <maps-available :id="rId" :type="type" :viewer-selected-i-d="reaction.id" />
            <gem-contact :id="rId" :type="type" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import Loader from '@/components/Loader';
import NotFound from '@/components/NotFound';
import MapsAvailable from '@/components/explorer/gemBrowser/MapsAvailable';
import ExtIdTable from '@/components/explorer/gemBrowser/ExtIdTable';
import GemContact from '@/components/shared/GemContact';
import References from '@/components/shared/References';
import { buildCustomLink, reformatTableKey, capitalize, convertCamelCase, addMassUnit, reformatChemicalReactionHTML, equationSign } from '@/helpers/utils';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'Reaction',
  components: {
    NotFound,
    Loader,
    MapsAvailable,
    ExtIdTable,
    GemContact,
    References,
  },
  data() {
    return {
      rId: this.$route.params.id,
      type: 'reaction',
      mainTableKey: [
        { name: 'id' },
        { name: 'equation', modifier: this.reformatEquation },
        { name: 'isReversible', display: 'Reversible', modifier: this.reformatReversible },
        { name: 'quantitative', modifier: this.reformatQuant },
        { name: 'geneRule', display: 'Gene rule', modifier: this.reformatGenes },
        { name: 'ec', display: 'EC' },
        { name: 'compartments', display: 'Compartment(s)' },
        { name: 'subsystems', display: 'Subsystem(s)' },
      ],
      modelErrorMessage: '',
      showLoaderMessage: '',
      mapsAvailable: {},
      componentNotFound: false,
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      reaction: state => state.reactions.reaction,
      referenceList: state => state.reactions.referenceList,
      relatedReactions: state => state.reactions.relatedReactions,
    }),
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
      this.showLoaderMessage = 'Loading reaction data';
      this.rId = this.$route.params.id;
      try {
        const payload = { model: this.model, id: this.rId };
        await this.$store.dispatch('reactions/getReactionData', payload);
        this.componentNotFound = false;
        this.showLoaderMessage = '';
        await this.getRelatedReactions();
      } catch {
        this.componentNotFound = true;
        document.getElementById('search').focus();
      }
    },
    async getRelatedReactions() {
      try {
        const payload = { model: this.model, id: this.rId };
        await this.$store.dispatch('reactions/getRelatedReactionsForReaction', payload);
      } catch {
        this.$store.dispatch('reactions/clearRelatedReactions');
      }
    },
    reformatEquation() { return reformatChemicalReactionHTML(this.reaction, false, this.model.short_name); },
    reformatGenes() {
      if (!this.reaction.geneRule) {
        return '-';
      }
      let newGRnameArr = null;
      if (this.reaction.geneRule_wname) {
        newGRnameArr = this.reaction.geneRule_wname.split(/ +/).map(
          e => e.replace(/^\(+|\)+$/g, '')
        );
      }
      let newGR = this.reaction.geneRule;
      if (newGR) {
        let i = -1;
        const newGRArr = newGR.split(/ +/).map(
          (e) => {
            i += 1;
            if (e === 'or' || e === 'and') {
              return e;
            }
            const prefix = e[0] === '(' ? '(' : '';
            const suffix = e.slice(-1) === ')' ? ')' : '';
            const newE = e.replace(/^\(+|\)+$/g, '');
            const tag = newGRnameArr ? newGRnameArr[i] : newE;
            const customLink = buildCustomLink({ model: this.model.short_name, type: 'gene', id: newE, title: tag });
            return `${prefix}<span class="tag">${customLink}</span>${suffix}`;
          });
        newGR = newGRArr.join(' ');
      }
      return newGR;
    },
    formatQuantFieldName(name) { return `${name}:&nbsp;`; },
    reformatQuant() {
      const data = [];
      ['lowerBound', 'upperBound', 'objective_coefficient'].forEach((key) => {
        if (this.reaction[key] != null) {
          data.push(this.formatQuantFieldName(capitalize(convertCamelCase(key))));
          if (key === 'objective_coefficient') {
            data.push(addMassUnit(this.reaction[key]));
          } else {
            data.push(this.reaction[key]);
          }
          data.push('<span>&nbsp;&dash;&nbsp;</span>');
        }
      });
      let s = data.join(' ');
      if (s.endsWith('<span>&nbsp;&dash;&nbsp;</span>')) {
        s = s.slice(0, -31);
      }
      return s;
    },
    reformatReversible() { return this.reaction.reversible ? 'Yes' : 'No'; },
    reformatTableKey,
    reformatChemicalReactionHTML,
    equationSign,
  },
};
</script>

<style lang="scss"></style>
