<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div class="columns" v-else>
    <loader v-show="showLoader"></loader>
    <div class="reaction-table column is-10" v-show="!showLoader">
      <table v-if="reaction && Object.keys(reaction).length != 0" class="table main-table is-fullwidth">
        <tr v-for="el in mainTableKey">
          <td v-if="el.display" class="td-key">{{ el.display }}</td>
          <td v-else class="td-key">{{ reformatKey(el.name) }}</td>
          <td v-if="el.isComposite">
            <span v-html="el.modifier()"></span>
          </td>
          <td v-else-if="reaction[el.name]">
            <span v-if="el.modifier" v-html="el.modifier(reaction[el.name])">
            </span>
            <span v-else>
              {{ reaction[el.name] }}
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
    <div class="column">
      <div class="box has-text-centered">
        <div class="button is-info">
          <p><i class="fa fa-eye"></i> on Metabolic Viewer<p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import Loader from 'components/Loader';
import { default as EventBus } from '../event-bus';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../helpers/chemical-formatters';
import { reformatChemicalReaction } from '../helpers/compartment';

export default {
  name: 'reaction',
  props: ['model'],
  components: {
    Loader,
  },
  data() {
    return {
      rId: this.$route.params.id,
      mainTableKey: [
        { name: 'id', display: 'Model ID' },
        // { name: 'name', display: 'Name', modifier: chemicalName },
        { name: 'equation', modifier: this.reformatEquation },
        { name: 'is_reversible', display: 'Reversible', isComposite: true, modifier: this.reformatReversible },
        { name: 'quantitative', isComposite: true, modifier: this.reformatQuant },
        { name: 'modifiers', modifier: this.reformatModifiers },
        { name: 'ec', display: 'EC', modifier: this.reformatECLink },
        { name: 'compartment', isComposite: true, modifier: this.reformatCompartment },
        { name: 'subsystem_str', display: 'Subsystem', modifier: this.reformatSubsystemList },
        { name: 'sbo_id', display: 'SBO', modifier: this.reformatSBOLink },
      ],
      reaction: {},
      pmids: [],
      errorMessage: '',
      showLoader: true,
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
      this.rId = this.$route.params.id;
      this.load();
    },
    load() {
      axios.get(`${this.model}/reactions/${this.rId}/`)
      .then((response) => {
        this.showLoader = false;
        this.reaction = response.data.reaction;
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
      return this.reformatChemicalReaction(equation, this.reaction);
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
        html.push(`<span class="tag"><a class="e" name="${mod.id}">${mod.short_name}</a></span>`);
      }
      html.push('</div>');
      return html.join(' ');
    },
    reformatSubsystemList(substr) {
      // return l.join('; ');
      // TODO add route logic on url 'subsystem' query
      let str = '';
      for (const s of substr.split('; ')) {
        // str = str.concat('<a href="/?tab=1&subsystem=', a, '">', a, '</a>');
        str = str.concat(`<a class="s" name="${s}">`, s, '</a>');
      }
      return str;
    },
    formatQuantFieldName(name) {
      return `<span class="tag is-info">${name}</span>`;
    },
    reformatQuant() {
      const data = [];
      for (const key of ['upper_bound', 'lower_bound', 'objective_coefficient']) {
        if (this.reaction[key]) {
          data.push(this.formatQuantFieldName(this.reformatKey(key)));
          if (key === 'objective_coefficient') {
            data.push(this.reformatMass(this.reaction[key]));
          }
          data.push(this.reaction[key]);
        }
        data.push('<span>&nbsp;&nbsp;</span>');
      }
      return data.join(' ');
    },
    reformatCompartment() {
      const compartment = this.reaction.is_reversible ?
       this.reaction.compartment.replace('=>', '&#8660;') : this.reaction.compartment.replace('=>', '&#8680;');
      if (this.reaction.is_transport) {
        return `${compartment} (transport reaction)`;
      }
      return `${compartment}`;
    },
    reformatReversible() {
      if (this.reaction.is_reversible) {
        return 'Yes';
      }
      return 'No';
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
    $('body').on('click', 'a.e', function f() {
      EventBus.$emit('updateSelTab', 'enzyme', $(this).attr('name'));
    });
    $('body').on('click', 'a.s', function f() {
      EventBus.$emit('updateSelTab', 'subsystem', $(this).attr('name'));
    });
    this.setup();
  },
};
</script>

<style lang="scss">

</style>
