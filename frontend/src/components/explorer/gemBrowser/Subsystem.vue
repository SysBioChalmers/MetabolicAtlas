<template>
  <component-layout
    component-type="subsystem" :component-name="info.name"
    :external-dbs="info.externalDbs" query-component-action="subsystems/getSubsystemSummary"
  >
    <template v-slot:table>
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
    </template>
  </component-layout>
</template>


<script>

import { mapGetters, mapState } from 'vuex';
import ComponentLayout from '@/layouts/explorer/gemBrowser/ComponentLayout';
import { buildCustomLink, generateSocialMetaTags, reformatTableKey } from '@/helpers/utils';

export default {
  name: 'Subsystem',
  components: {
    ComponentLayout,
  },
  data() {
    return {
      sName: this.$route.params.id,
      mainTableKey: [
        { name: 'name', display: 'Name' },
      ],
      showFullMetabolite: false,
      showFullGene: false,
      displayedMetabolite: 40,
      displayedGene: 40,
    };
  },
  metaInfo() {
    if (!this.model || !this.info.name) {
      return {};
    }

    const title = `${this.info.name}, Subsystem in ${this.model.short_name}`;
    const description = `The subsystem ${this.info.name} in ${this.model.short_name} (version ${this.model.version}) can be found in ${this.info.compartments.length} compartments, and contains ${this.metabolites.length} metabolites and ${this.genes.length} genes.`;

    return {
      title,
      meta: generateSocialMetaTags({ title, description }),
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
  methods: {
    reformatKey(k) { return reformatTableKey(k); },
  },
};
</script>

<style lang="scss"></style>
