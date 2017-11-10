<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else class="reaction-table">
    <table v-if="info && Object.keys(info).length != 0" class="table main-table">
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
    <span class="subtitle">References</span>
    <table v-if="pmids && Object.keys(pmids).length != 0" id="main-table" class="table">
      <tr v-for="ref in reformatRefs(pmids)">
        <a :href="ref.link">
          <td v-if="ref.title" class="td-key">{{ ref.pmid }}</td>
          <td v-if="ref.formatted">{{ ref.formatted }}</td>
        </a>
      </tr>
    </table>
    <div v-else>No references found</div>
  </div>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import { default as EventBus } from '../event-bus';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../helpers/chemical-formatters';
import { reformatChemicalReaction } from '../helpers/compartment';

export default {
  name: 'reaction',
  data() {
    return {
      rId: this.$route.query.id,
      mainTableKey: [
        { name: 'id', display: 'Identifier' },
        { name: 'name', display: 'Name', modifier: chemicalName },
        { name: 'compartment' },
        { name: 'subsystem', modifier: this.reformatSubsystemList },
        { name: 'equation', modifier: this.reformatEquation },
        { name: 'quantitative', isComposite: true, modifier: this.reformatQuant },
        { name: 'modifiers', modifier: this.reformatModifiers },
        { name: 'ec', display: 'EC', modifier: this.reformatECLink },
        { name: 'sbo_id', display: 'SBO', modifier: this.reformatSBOLink },
      ],
      info: {},
      pmids: [],
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
        this.info = response.data.reaction;
        this.pmids = response.data.pmids;
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
    reformatEquation(equation) {
      return this.reformatChemicalReaction(equation, this.info);
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
      html.push('<div class="tags">');
      for (const mod of mods) {
        html.push(`<span class="tag"><a href="/?tab=3&id=${mod.id}">${mod.short_name}</a></span>`);
      }
      html.push('</div>');
      return html.join(' ');
    },
    reformatSubsystemList(l) {
      // return l.join('; ');
      // TODO add route logic on url 'subsystem' query
      let str = '';
      for (const a of l) {
        // str = str.concat('<a href="/?tab=1&subsystem=', a, '">', a, '</a>');
        str = str.concat('<a href="#">', a, '</a>');
      }
      return str;
    },
    formatQuantFieldName(name) {
      return `<span class="tag is-info">${name}</span>`;
    },
    reformatQuant() {
      const data = [];
      for (const key of ['upper_bound', 'lower_bound', 'objective_coefficient']) {
        if (this.info[key]) {
          data.push(this.formatQuantFieldName(this.reformatKey(key)));
          if (key === 'objective_coefficient') {
            data.push(this.reformatMass(this.info[key]));
          }
          data.push(this.info[key]);
        }
        data.push('<span>&nbsp;&nbsp;</span>');
      }
      return data.join(' ');
    },
    chemicalFormula,
    chemicalName,
    chemicalNameExternalLink,
    reformatChemicalReaction,
    reformatRefs(refs) {
      const outrefs = [];
      for (const key of Object.keys(refs)) {
        const formattedref = {};
        const ref = refs[key];
        formattedref.pmid = key;
        formattedref.link = `http://pubmed.com/${key}`;
        const text = [];
        if (ref.pubdate) {
          ref.pubyear = ref.pubdate.substring(0, 4);
        }
        const fields = ['sortfirstauthor', 'lastauthor', 'pubyear', 'fulljournalname', 'title'];
        for (const field of fields) {
          if (ref[field]) {
            text.push(ref[field]);
          }
        }
        formattedref.formatted = text.join(', ');
        outrefs.push(formattedref);
      }
      return outrefs;
    },
  },
  beforeMount() {
    $('body').on('click', 'td rc', function f() {
      EventBus.$emit('updateSelTab', 'metabolite', $(this).attr('id'));
    });
    this.setup();
  },
};
</script>

<style lang="scss">

</style>
