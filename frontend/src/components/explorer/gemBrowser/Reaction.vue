<template>
<component-layout
    :component-type="type" :component-name="reaction.id"
    :external-dbs="reaction.externalDbs" query-component-action="reactions/getReactionData"
    :viewer-selected-i-d="reaction.id" :include-reaction-table="false"
    :reference-list="referenceList"
     @doAfterLoad="doAfterLoad"
  >
    <template v-slot:table>
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
    </template>
  </component-layout>
</template>

<script>
import { mapState } from 'vuex';
import ComponentLayout from '@/layouts/explorer/gemBrowser/ComponentLayout';
import { buildCustomLink, reformatTableKey, capitalize, convertCamelCase, addMassUnit, reformatChemicalReactionHTML, equationSign } from '@/helpers/utils';

export default {
  name: 'Reaction',
  components: {
    ComponentLayout,
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
      modelNotFound: false,
      showLoaderMessage: '',
      mapsAvailable: {},
      componentNotFound: false,
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
  methods: {
    async doAfterLoad() {
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
            const newEName = e.replace(/^\(+|\)+$/g, '');
            const newEId = this.reaction.genes.find(g => g.name === newEName).id;
            const tag = newGRnameArr ? newGRnameArr[i] : newEName;
            const customLink = buildCustomLink({ model: this.model.short_name, type: 'gene', id: newEId, title: tag });
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
