<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else>
    <div class="columns">
      <div class="column">
        <h3 class="title is-size-3">Reaction {{ reaction.id }}</h3>
      </div>
    </div>
    <div class="columns" v-show="showLoader">
      <loader></loader>
    </div>
    <div class="columns is-multiline is-variable is-8" v-show="!showLoader">
      <div class="reaction-table column is-10-widescreen is-9-desktop is-full-tablet">
        <table v-if="reaction && Object.keys(reaction).length != 0" class="table main-table is-fullwidth">
          <tr v-for="el in mainTableKey[model.database_name]">
            <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
            <td v-else-if="el.name == 'id'" class="td-key has-background-primary has-text-white-bis">{{ model.short_name }} ID</td>
            <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
            <td v-if="'isComposite' in el">
              <span v-html="el.modifier()"></span>
            </td>
            <td v-else-if="reaction[el.name]">
              <span v-if="'modifier' in el" v-html="el.modifier(reaction[el.name])">
              </span>
              <span v-else>
                {{ reaction[el.name] }}
              </span>
            </td>
            <td v-else> - </td>
          </tr>
        </table>
        <template v-if="hasExternalID">
          <br>
          <h4 class="title is-size-4">External IDs</h4>
          <table v-if="reaction && Object.keys(reaction).length != 0" id="ed-table" class="table is-fullwidth">
            <tr v-for="el in externalIDTableKey[model.database_name]" v-if="reaction[el.name] && reaction[el.link]">
              <td v-if="'display' in el" class="td-key has-background-primary has-text-white-bis" v-html="el.display"></td>
              <td v-else class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(el.name) }}</td>
              <td>
                <a :href="`${reaction[el.link]}`" target="_blank">{{ reaction[el.name] }}</a>
              </td>
            </tr>
          </table>
        </template>
        <br>
        <template v-if="formattedRef.length != 0">
          <h4 class="title is-size-4">References (PMID)</h4>
          <table class="main-table table">
            <tr v-for="oneRef in formattedRef">
              <td v-if="oneRef.title" class="td-key has-background-primary has-text-white-bis">{{ oneRef.pmid }}</td>
              <a :href="oneRef.link" target="_blank">
                <td>
                  <template v-for="author in oneRef.authors">
                    {{ author }},
                  </template>
                  {{ oneRef.year }}. <i>{{ oneRef.title }}</i>
                  {{ oneRef.journal }}
                </td>
              </a>
            </tr>
          </table>
        </template>
        <template v-else>
          <p>No PMID references found</p>
        </template>
      </div>
      <div class="column is-2-widescreen is-3-desktop is-full-tablet has-text-centered">
        <div class="card">
          <header class="card-header has-text-centered">
            <p class="card-header-title has-text-primary has-text-weight-bold is-size-5">
              <span class="icon is-medium"><i class="fa fa-map-o"></i></span>&nbsp;
              <span>{{ messages.mapViewerName }}</span>
            </p>
            <a href="#" class="card-header-icon" aria-label="more options">
            </a>
          </header>
          <div class="card-content" style="padding: 0.5rem;">
            <div class="content has-text-left is-paddingless" v-if="Object.keys(mapsAvailable).length !== 0">
              <ul> 2D maps
                <template v-for="map in mapsAvailable['2d']['compartment']">
                  <li><router-link  :to="{ path: `/explore/map-viewer/${model.database_name}/${map[2]}/${map[0]}/${rId}?dim=2d` }">
                    {{ map[1] }}
                  </router-link></li>
                </template>
                <template v-for="map in mapsAvailable['2d']['subsystem']">
                  <li><router-link  :to="{ path: `/explore/map-viewer/${model.database_name}/${map[2]}/${map[0]}/${rId}?dim=2d` }">
                    {{ map[1] }}
                  </router-link></li>
                </template>
              </ul>
              <ul>3D maps
                 <template v-for="map in mapsAvailable['3d']['compartment']">
                  <li><router-link :to="{ path: `/explore/map-viewer/${model.database_name}/${map[2]}/${map[0]}/${rId}?dim=3d` }">
                    {{ map[1] }}
                  </router-link></li>
                </template>
                <template v-for="map in mapsAvailable['3d']['subsystem']">
                  <li><router-link :to="{ path: `/explore/map-viewer/${model.database_name}/${map[2]}/${map[0]}/${rId}?dim=3d` }">
                    {{ map[1] }}
                  </router-link></li>
                </template>
              </ul>
            </div>
          </div>
          <footer class="card-footer">
          </footer>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import Loader from 'components/Loader';
import { default as EventBus } from '../../../event-bus';
import { chemicalFormula, chemicalName, chemicalNameExternalLink } from '../../../helpers/chemical-formatters';
import { reformatTableKey, addMassUnit, reformatSBOLink, reformatECLink, reformatCompEqString } from '../../../helpers/utils';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'reaction',
  props: ['model'],
  components: {
    Loader,
  },
  data() {
    return {
      messages,
      rId: this.$route.params.id,
      mainTableKey: {
        hmr2: [
          { name: 'id' },
          { name: 'equation', modifier: this.reformatEquation },
          { name: 'is_reversible', display: 'Reversible', isComposite: true, modifier: this.reformatReversible },
          { name: 'quantitative', isComposite: true, modifier: this.reformatQuant },
          { name: 'gene_rule', isComposite: true, display: 'Enzymes', modifier: this.reformatModifiers },
          { name: 'ec', display: 'EC', modifier: this.reformatECLink },
          { name: 'compartment', isComposite: true, modifier: this.reformatCompartment },
          { name: 'subsystem', display: 'Subsystem', modifier: this.reformatSubsystemList },
          { name: 'sbo_id', display: 'SBO', modifier: this.reformatSBOLink },
        ],
        yeast: [
          { name: 'id' },
          { name: 'equation', modifier: this.reformatEquation },
          { name: 'is_reversible', display: 'Reversible', isComposite: true, modifier: this.reformatReversible },
          { name: 'quantitative', isComposite: true, modifier: this.reformatQuant },
          { name: 'gene_rule', isComposite: true, display: 'Enzymes', modifier: this.reformatModifiers },
          { name: 'ec', display: 'EC', modifier: this.reformatECLink },
          { name: 'compartment', isComposite: true, modifier: this.reformatCompartment },
          { name: 'subsystem', display: 'Subsystem', modifier: this.reformatSubsystemList },
        ],
      },
      externalIDTableKey: {
        hmr2: [
          { name: 'mnxref_id', display: 'MNXREF ID', link: 'mnxref_link' },
        ],
        yeast: [],
      },
      reaction: {},
      errorMessage: '',
      showLoader: true,
      mapsAvailable: {},
      formattedRef: [],
    };
  },
  created() {
    $('body').on('click', 'a.e', function f() {
      EventBus.$emit('GBnavigateTo', 'enzyme', $(this).attr('name'));
    });
    $('body').on('click', 'a.s', function f() {
      EventBus.$emit('GBnavigateTo', 'subsystem', $(this).attr('name'));
    });
  },
  beforeMount() {
    this.setup();
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.$route.path.includes('/reaction/')) {
        if (this.rId !== this.$route.params.id) {
          this.setup();
        }
      }
    },
  },
  computed: {
    hasExternalID() {
      for (const item of this.externalIDTableKey[this.model.database_name]) {
        if (this.reaction[item.name] && this.reaction[item.link]) {
          return true;
        }
      }
      return false;
    },
  },
  methods: {
    setup() {
      this.rId = this.$route.params.id;
      this.load();
      this.getAvailableMaps();
    },
    load() {
      axios.get(`${this.model.database_name}/reaction/${this.rId}/`)
      .then((response) => {
        this.showLoader = false;
        this.reaction = response.data.reaction;
        this.reformatRefs(response.data.pmids);
      })
      .catch(() => {
        this.errorMessage = messages.notFoundError;
      });
    },
    getAvailableMaps() {
      axios.get(`${this.model.database_name}/available_maps/${this.rId}`)
      .then((response) => {
        this.mapsAvailable = response.data;
      }).catch(() => {
      });
    },
    reformatEquation() { return this.$parent.$parent.reformatChemicalReactionLink(this.reaction); },
    reformatModifiers() {
      let newGRnameArr = null;
      if (this.reaction.name_gene_rule) {
        newGRnameArr = this.reaction.name_gene_rule.split(/ and | or /).map(
        e => e.replace(/^\(+|\)+$/g, '')
        );
      }

      let newGR = this.reaction.gene_rule;
      if (newGR) {
        const newGRArr = newGR.split(/ and | or /).map(
          e => e.replace(/^\(+|\)+$/g, '')
          );
        for (let i = 0, l = newGRArr.length; i < l; i += 1) {
          let e;
          if (newGRnameArr) {
            e = `<span class="tag"><a class="e is-size-6" name="${newGRArr[i]}">${newGRnameArr[i]}</a></span>`;
          } else {
            e = `<span class="tag"><a class="e is-size-6" name="${newGRArr[i]}">${newGRArr[i]}</a></span>`;
          }
          const re = new RegExp(`\\s${newGRArr[i]}|${newGRArr[i]}\\s`);
          newGR = newGR.replace(re, e);
        }
      }
      return newGR;
    },
    reformatSubsystemList(substr) {
      let str = '';
      for (const s of substr.split('; ')) {
        str = str.concat(`<a class="s" name="${s}">`, s, '</a><br>');
      }
      if (str) {
        str = str.slice(0, -4);
      }
      return str;
    },
    formatQuantFieldName(name) { return `${name}:&nbsp;`; },
    reformatQuant() {
      const data = [];
      for (const key of ['lower_bound', 'upper_bound', 'objective_coefficient']) {
        if (this.reaction[key] != null) {
          data.push(this.formatQuantFieldName(this.reformatTableKey(key)));
          if (key === 'objective_coefficient') {
            data.push(addMassUnit(this.reaction[key]));
          } else {
            data.push(this.reaction[key]);
          }
          data.push('<span>&nbsp;&dash;&nbsp;</span>');
        }
      }
      let s = data.join(' ');
      if (s.endsWith('<span>&nbsp;&dash;&nbsp;</span>')) {
        s = s.slice(0, -31);
      }
      return s;
    },
    reformatCompartment() {
      const compartmentEq =
        this.reformatCompEqString(this.reaction.compartment);
      if (this.reaction.is_transport) {
        return `${compartmentEq} (transport reaction)`;
      }
      return `${compartmentEq}`;
    },
    reformatReversible() { return this.reaction.is_reversible ? 'Yes' : 'No'; },
    reformatRefs(refs) {
      for (const i of refs) {
        axios.get(`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=${i.pmid}`)
        .then((response) => {
          const details = response.data.result[i.pmid];
          const newRef = {};
          newRef.pmid = i.pmid;
          newRef.link = `http://pubmed.com/${i.pmid}`;
          if (details.pubdate) {
            newRef.year = details.pubdate.substring(0, 4);
          }
          newRef.authors = details.authors.map(e => (e.authtype === 'Author' ? e.name : null));
          newRef.journal = details.fulljournalname;
          newRef.title = details.title;
          this.formattedRef.push(newRef);
        })
        .catch(() => {
          this.errorMessage = messages.notFoundError;
        });
      }
    },
    viewReactionOnMap(reactionID) {
      EventBus.$emit('viewReactionOnMap', reactionID);
    },
    chemicalFormula,
    chemicalName,
    chemicalNameExternalLink,
    reformatSBOLink,
    reformatTableKey,
    reformatECLink,
    reformatCompEqString,
  },
};
</script>

<style lang="scss"></style>
