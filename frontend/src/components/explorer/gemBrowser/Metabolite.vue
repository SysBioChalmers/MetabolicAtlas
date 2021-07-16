<template>
  <component-layout
    component-type="metabolite" :component-name="metabolite.name"
    :compartment-name="(metabolite && metabolite.compartment) ? metabolite.compartment.name : ''"
    :external-dbs="metabolite.externalDbs" query-component-action="metabolites/getMetaboliteData"
    :interaction-partner="true" :viewer-selected-i-d="metabolite.id"
    :related-met-count="relatedMetabolites.length" :is-metabolite="true"
    :selected-elm-id="true"
    @handleCallback="handleCallback"
  >
    <template v-slot:table>
      <table v-if="metabolite" class="table main-table is-fullwidth">
        <tr v-for="el in mainTableKey" :key="el.name">
          <td v-if="el.display"
              class="td-key has-background-primary has-text-white-bis" v-html="el.display">
          </td>
          <td v-else-if="el.name === 'id'"
              class="td-key has-background-primary has-text-white-bis">
            {{ model ? model.short_name : '' }} ID
          </td>
          <td v-else class="td-key has-background-primary has-text-white-bis">
            {{ reformatTableKey(el.name) }}
          </td>
          <td v-if="metabolite[el.name] !== null">
            <span v-if="el.name === 'formula'"
                  v-html="chemicalFormula(metabolite[el.name], metabolite.charge)">
            </span>
            <span v-else-if="el.modifier" v-html="el.modifier(metabolite[el.name])">
            </span>
            <span v-else-if="el.name === 'compartment' && metabolite[el.name]">
              <!-- eslint-disable-next-line max-len -->
              <router-link :to="{ name: 'compartment', params: { model: model.short_name, id: metabolite[el.name].id } }"
              >{{ metabolite[el.name].id }}</router-link>
            </span>
            <span v-else>
              {{ metabolite[el.name] }}
            </span>
          </td>
          <td v-else> - </td>
        </tr>
        <tr v-if="relatedMetabolites.length !== 0">
          <td class="td-key has-background-primary has-text-white-bis">Related metabolite(s)</td>
          <td>
            <span v-for="(rm, i) in relatedMetabolites" :key="rm.id">
              <br v-if="i !== 0">
              <!-- eslint-disable-next-line max-len -->
              <router-link :to="{ name: 'metabolite', params: { model: model.short_name, id: rm.id } }">
                {{ rm.fullName }}
              </router-link> in {{ rm.compartment.name }}
            </span>
          </td>
        </tr>
      </table>
    </template>
    <template v-slot:chebi>
      <div v-if="chebiImageLink"
           class="column is-3-widescreen is-2-desktop is-full-tablet has-text-centered px-2">
        <a :href="metabolite.externalDbs.ChEBI[0].url" target="_blank">
          <img id="chebi-img" :src="chebiImageLink" class="hoverable" />
          <a :href="metabolite.externalDbs.ChEBI[0].url" target="_blank" style="display: block;">
            {{ metabolite.name }} via ChEBI</a>
        </a>
      </div>
    </template>
  </component-layout>
</template>

<script>
import axios from 'axios';
import { mapState } from 'vuex';
import ComponentLayout from '@/layouts/explorer/gemBrowser/ComponentLayout';
import { chemicalFormula } from '@/helpers/chemical-formatters';
import { generateSocialMetaTags, reformatTableKey } from '@/helpers/utils';

export default {
  name: 'Metabolite',
  components: {
    ComponentLayout,
  },
  data() {
    return {
      metaboliteId: this.$route.params.id,
      mainTableKey: [
        { name: 'id' },
        { name: 'name' },
        { name: 'alternateName', display: 'Alternate name' },
        { name: 'synonyms' },
        { name: 'description' },
        { name: 'formula' },
        { name: 'charge' },
        { name: 'inchi', display: 'InChI' },
        { name: 'compartment' },
      ],
      activePanel: 'table',
      chebiImageLink: null,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      metabolite: state => state.metabolites.metabolite,
      relatedMetabolites: state => state.metabolites.relatedMetabolites,
    }),
  },
  metaInfo() {
    if (!this.model || !this.metabolite.name) {
      return {};
    }

    const title = `${this.metabolite.name}, Metabolite in ${this.model.short_name}`;
    const description = `The metabolite ${this.metabolite.name} in ${this.model.short_name} (version ${this.model.version}) can be found in the ${this.metabolite.compartment.name} compartment and the ${this.metabolite.subsystems[0].name} subsystem.`;

    return {
      title,
      meta: generateSocialMetaTags({ title, description }),
      script: [{
        type: 'application/ld+json',
        json: {
          '@context': 'http://schema.org',
          '@id': `https://metabolicatlas.org/explore/Human-GEM/gem-browser/metabolite/${this.metabolite.id}`,
          '@type': 'MolecularEntity',
          'dct:conformsTo': 'https://bioschemas.org/profiles/MolecularEntity/0.5-RELEASE',
          identifier: this.metabolite.id,
          name: this.metabolite.name,
          url: `https://metabolicatlas.org/explore/Human-GEM/gem-browser/metabolite/${this.metabolite.id}`,
        },
      }],
    };
  },
  methods: {
    async handleCallback() {
      if (this.metabolite.externalDbs.ChEBI) {
        const link = `https://www.ebi.ac.uk/chebi/displayImage.do?defaultImage=true&imageIndex=0&chebiId=${this.metabolite.externalDbs.ChEBI[0].id.slice(6)}`;
        const { data } = await axios.get(link);
        if (data !== '') {
          this.chebiImageLink = `${link}&dimensions=400`;
        }
      }

      try {
        const payload = { model: this.model, id: this.metaboliteId };
        await this.$store.dispatch('metabolites/getRelatedMetabolites', payload);
      } catch {
        this.$store.dispatch('metabolites/clearRelatedMetabolites');
      }
    },
    reformatTableKey(k) { return reformatTableKey(k); },
    chemicalFormula,
  },
};
</script>

<style lang="scss">
#chebi-img {
   border: 1px solid $grey-lighter;
}
</style>
