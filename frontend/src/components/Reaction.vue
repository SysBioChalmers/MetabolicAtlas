<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else class="reaction-table">
    <table v-if="info && Object.keys(info).length != 0" id="main-table" class="table">
      <tr v-for="el in mainTableKey">
        <td v-if="el.display" class="td-key">{{ el.display }}</td>
        <td v-else class="td-key">{{ reformatKey(el.name) }}</td>
        <td v-if="el.isComposite">
          <span v-html="el.modifier()"></span>
        </td>
        <td v-else-if="info[el.name]">
          <span v-if="el.modifier" v-html="el.modifier(info[el.name])">
          </span>
          <span v-else>
            {{ info[el.name] }}
          </span>
        </td>
        <td v-else> - </td>
      </tr>
    </table>
  </div>
</template>

<script>
import axios from 'axios';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../helpers/chemical-formatters';

export default {
  name: 'reaction',
  data() {
    return {
      rId: this.$route.query.id,
      mainTableKey: [
        { name: 'id', display: 'Identifier' },
        { name: 'name', display: 'Name', modifier: chemicalName },
        { name: 'compartment' },
        { name: 'subsystem', modifier: this.reformatList },
        { name: 'equation', modifier: chemicalName },
        { name: 'quantitative_stuff', isComposite: true, modifier: this.reformatQuant },
        { name: 'modifiers', modifier: this.reformatModifiers },
        { name: 'reactants', modifier: this.reformatCount },
        { name: 'products', modifier: this.reformatCount },
        { name: 'ec', display: 'EC', modifier: this.reformatECLink },
        { name: 'sbo_id', display: 'SBO', modifier: this.reformatSBOLink },
      ],
      info: {},
      errorMessage: '',
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  methods: {
    setup() {
      this.rId = this.$route.query.id;
      this.load();
    },
    load() {
      axios.get(`reactions/${this.rId}/`)
      .then((response) => {
        this.info = response.data;
      })
      .catch(() => {
        this.errorMessage = this.$t('notFoundError');
      });
    },
    reformatID(id) {
      return id.slice(2);
    },
    reformatKey(k) {
      return `${k[0].toUpperCase()}${k.slice(1).replace('_', ' ')}`;
    },
    reformatSBOLink(s, link) {
      if (link) {
        return `<a href="${link}" target="_blank">${s}</a>`;
      }
      if (s.startsWith('SBO')) {
        return `<a href="http://www.ebi.ac.uk/sbo/main/${s}" target="_blank">${s}</a>`;
      }
      return `<a href="${s}" target="_blank">${s}</a>`;
    },
    reformatECLink(s) {
      const ec = s.split(';');
      let l = '';
      for (let i = 0; i < ec.length; i += 1) {
        const nr = ec[i].replace('EC:', '');
        l = l.concat(`<a href="http://www.brenda-enzymes.org/enzyme.php?ecno=${nr}" target="_blank">${ec[i]}</a> `);
      }
      return l;
    },
    reformatMass(s) {
      return `${s} g/mol`;
    },
    reformatModifiers(mods) {
      const html = [];
      html.push('<div class="field is-grouped is-grouped-multiline">');
      for (const mod of mods) {
        html.push(`<div class="control"><div class="tags has-addons">
          <span class="tag"><a href="/?tab=3&reaction_component_id=${mod.id}">${mod.short_name}</a></span></div></div>`);
      }
      html.push('</div>');
      return html.join(' ');
    },
    reformatList(l) {
      return l.join('; ');
    },
    reformatCount(e) {
      return e.length;
    },
    formatQuantFieldName(name) {
      return `<span class="tag is-info">${name}</span>`;
    },
    reformatQuant() {
      const data = [];
      for (const key of ['upper_bound', 'lower_bound', 'objective_coefficient']) {
        data.push(this.formatQuantFieldName(this.reformatKey(key)));
        if (this.info[key]) {
          if (key === 'objective_coefficient') {
            data.push(this.reformatMass(this.info[key]));
          }
          data.push(this.info[key]);
        } else {
          data.push('-');
        }
        data.push('<span>&nbsp;&nbsp;</span>');
      }
      return data.join(' ');
    },
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

.reaction-table {
  #main-table tr td.td-key {
    background: #64CC9A;
    width: 150px;
    color: white;
  }
}

</style>
