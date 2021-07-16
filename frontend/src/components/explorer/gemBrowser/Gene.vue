<template>
  <component-layout
    component-type="gene" :component-name="gene.geneName"
    :external-dbs="gene.externalDbs" query-component-action="genes/getGeneData"
    :interaction-partner="true" :viewer-selected-i-d="gene.id"
  >
    <template v-slot:table>
      <table v-if="gene && Object.keys(gene).length !== 0" class="table main-table is-fullwidth">
        <tr v-for="el in mainTableKey" :key="el.name">
          <td v-if="'display' in el"
              class="td-key has-background-primary has-text-white-bis"
              v-html="el.display"></td>
          <td v-else-if="el.name === 'id'"
              class="td-key has-background-primary has-text-white-bis">
            {{ model? model.short_name : '' }} ID
          </td>
          <td v-else
              class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
          <td v-if="gene[el.name]">
            <span v-if="'modifier' in el" v-html="el.modifier(gene)">
            </span>
            <span v-else>
              {{ gene[el.name] }}
            </span>
          </td>
          <td v-else> - </td>
        </tr>
      </table>
    </template>
  </component-layout>
</template>


<script>
import { mapGetters, mapState } from 'vuex';
import ComponentLayout from '@/layouts/explorer/gemBrowser/ComponentLayout';
import { generateSocialMetaTags, reformatTableKey } from '@/helpers/utils';

export default {
  name: 'Gene',
  components: {
    ComponentLayout,
  },
  data() {
    return {
      showReactionLoader: true,
      geneId: '',
      mainTableKey: [
        { name: 'id' },
        { name: 'name', display: 'Gene&nbsp;name' },
        { name: 'alternateName', display: 'Alternate&nbsp;name' },
        { name: 'synonyms' },
        { name: 'function' },
      ],
      limitReaction: 200,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      gene: state => state.genes.gene,
    }),
    ...mapGetters({
      geneName: 'genes/geneName',
    }),
  },
  metaInfo() {
    if (!this.model || !this.gene.geneName) {
      return {};
    }

    const title = `${this.gene.geneName}, Gene in ${this.model.short_name}`;
    const description = `The gene ${this.gene.geneName} in ${this.model.short_name} (version ${this.model.version}) can be found in the ${this.gene.compartments[0].name} compartment and the ${this.gene.subsystems[0].name} subsystem.`;

    return {
      title,
      meta: generateSocialMetaTags({ title, description }),
      script: [{
        type: 'application/ld+json',
        json: {
          '@context': 'http://schema.org',
          '@id': `https://metabolicatlas.org/explore/Human-GEM/gem-browser/gene/${this.gene.id}`,
          '@type': 'Gene',
          'dct:conformsTo': 'https://bioschemas.org/profiles/Gene/1.0-RELEASE',
          identifier: this.gene.id,
          name: this.gene.geneName,
        },
      }],
    };
  },
  methods: {
    reformatTableKey(k) { return reformatTableKey(k); },
  },
};

</script>

<style lang="scss">
</style>
