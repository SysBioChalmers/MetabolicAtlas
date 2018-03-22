<template>
  <div v-if="errorMessage" class="columns">
    <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
      {{ errorMessage }}
    </div>
  </div>
  <div v-else>
    <loader v-show="showLoader"></loader>
    <div v-show="!showLoader">
      <div class="subsystem-table">
        <table v-if="info && Object.keys(info).length != 0" class="table main-table">
          <tr class="m-row" v-for="el in mainTableKey">
            <td v-if="el.display" class="td-key">{{ el.display }}</td>
            <td v-else class="td-key">{{ reformatKey(el.name) }}</td>
            <td v-if="info[el.name]">
              <span v-if="el.modifier" v-html="el.modifier(info[el.name])">
              </span>
              <span v-else>
                {{ info[el.name] }}
              </span>
            </td>
            <td v-else> - </td>
          </tr>
          <tr>
            <td class="td-key">Compartments</td>
            <td>{{ info['compartment'].join(', ') }}</td>
          </tr>
          <tr>
            <td class="td-key">Metabolites</td>
            <td v-html="metabolitesListHtml"></td>
          </tr>
          <tr>
            <td class="td-key">Enzymes</td>
            <td v-html="enzymesListHtml"></td>
          </tr>
        </table>
        <h3 class="title is-3">Reactions</h3>
        <reaction-table :reactions="reactions" :showSubsystem="false"></reaction-table>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import Loader from 'components/Loader';
import ReactionTable from 'components/ReactionTable';
import { default as EventBus } from '../event-bus';

export default {
  name: 'subsystem',
  components: {
    ReactionTable,
    Loader,
  },
  props: ['model'],
  data() {
    return {
      sName: this.$route.params.id,
      showLoader: false,
      info: {},
      metabolites: [],
      enzymes: [],
      reactions: [],
      errorMessage: '',
      mainTableKey: [
        { name: 'name', display: 'Name' },
        { name: 'system' },
      ],
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.setup();
    },
  },
  computed: {
    metabolitesListHtml() {
      const l = ['<span class="tags">'];
      this.metabolites.sort((a, b) => (a.short_name < b.short_name ? -1 : 1));
      for (const m of this.metabolites) {
        l.push(`<span id="${m.id}" class="tag rcm"><a>${m.short_name}[${m.id.substr(m.id.length - 1)}]</a></span>`);
      }
      l.push('</span>');
      return l.join('');
    },
    enzymesListHtml() {
      const l = ['<span class="tags">'];
      this.enzymes.sort((a, b) => (a.short_name < b.short_name ? -1 : 1));
      for (const e of this.enzymes) {
        l.push(`<span id="${e.id}" class="tag rce"><a>${e.short_name}</a></span>`);
      }
      l.push('</span>');
      return l.join('');
    },
  },
  methods: {
    setup() {
      this.sName = this.$route.params.id;
      this.load();
    },
    load() {
      this.showLoader = true;
      axios.get(`${this.model}/subsystem/${this.sName}/`)
      .then((response) => {
        this.info = response.data.subsystemAnnotations;
        this.metabolites = response.data.metabolites;
        this.enzymes = response.data.enzymes;
        this.reactions = response.data.reactions;
        this.showLoader = false;
      })
      .catch(() => {
        this.errorMessage = this.$t('notFoundError');
      });
    },
    getMetabolite() {
      return this.metabolites;
    },
    reformatKey(k) {
      return `${k[0].toUpperCase()}${k.slice(1).replace('_', ' ')}`;
    },
  },
  beforeMount() {
    $('body').on('click', 'span .rcm', function f() {
      EventBus.$emit('updateSelTab', 'metabolite', $(this).attr('id'));
    });
    $('body').on('click', 'span .rce', function f() {
      EventBus.$emit('updateSelTab', 'enzyme', $(this).attr('id'));
    });
    this.setup();
  },
};
</script>

<style lang="scss">



</style>
