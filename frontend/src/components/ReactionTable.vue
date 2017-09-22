<template>
  <div class="container reaction-table">
    <div class="field">
      <span class="tag">
        # Reaction(s): {{ reactions.length }}
      </span>
      <span class="tag">
        # Transport reaction(s): {{ transportReactionCount }}
      </span>
      <span v-show="reactions.length==200" class="tag is-danger is-pulled-right">
        {{ $t('tooManyReactionsTable') }}
      </span>
    </div>
    <table class="table is-bordered is-striped is-narrow" ref="table">
      <thead>
        <tr style="background: #F8F4F4">
          <th class="is-unselectable"
          v-for="f in fields" v-show="f.name !== 'cp' || showCP"
            @click="sortBy(f.name)">{{ f.display }}
            </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, index) in sortedReactions">
          <td>
            <a @click="viewReaction(r.id)">{{ r.id }}</a>
          </td>
          <td v-html="reformatChemicalReactionHTML(r.equation, r)"></td>
          <td>
            <a v-for="(m, index) in r.modifiers" v-on:click.prevent="viewEnzyneReactions(m)"
            >{{ index == 0 ? m.short_name : `, ${m.short_name}` }}</a></td>
          <td v-show="showCP">{{ r.cp }}</td>
          <td>{{ r.subsystem.join('; ') }}</td>
          <td v-html="">{{ r.compartment }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import $ from 'jquery';
import { default as EventBus } from '../event-bus';
import { default as compare } from '../helpers/compare';
import { chemicalReaction } from '../helpers/chemical-formatters';
import { reformatChemicalReaction } from '../helpers/compartment';

export default {
  name: 'reaction-table',
  props: ['reactions', 'selectedElmId'],
  data() {
    return {
      showCP: false,
      fields: [{
        display: 'Reaction ID',
        name: 'id',
      }, {
        display: 'Equation',
        name: 'equation',
      }, {
        display: 'Modifiers',
        name: 'modifiers',
      }, {
        display: 'C/P',
        name: 'cp',
      }, {
        display: 'Subsystem',
        name: 'subsystem',
      }, {
        display: 'Compartment',
        name: 'compartment',
      }],
      sortedReactions: [],
      sortAsc: true,
    };
  },
  watch: {
    reactions() {
      // create consume/produce column
      // TODO do this at the dababase level
      if (this.selectedElmId) {
        this.showCP = true;
        for (const reaction of this.reactions) {
          const boolC = reaction.reactants.map(x => x.id).includes(this.selectedElmId);
          const boolP = reaction.products.map(x => x.id).includes(this.selectedElmId);
          reaction.cp = '';
          if (boolC) {
            reaction.cp = 'consume';
            if (boolP) {
              reaction.cp += '/produce';
            }
          } else if (boolP) {
            reaction.cp = 'produce';
          }
        }
      }
      this.sortedReactions = this.reactions;
    },
  },
  computed: {
    transportReactionCount() {
      return this.reactions.filter(r => r.compartment.includes('=>')).length;
    },
  },
  methods: {
    formatChemicalReaction(v) {
      return chemicalReaction(v);
    },
    reformatChemicalReactionHTML(v, r) {
      return reformatChemicalReaction(this.formatChemicalReaction(v), r);
    },
    viewEnzyneReactions: function viewEnzyneReactions(modifier) {
      if (modifier) {
        EventBus.$emit('updateSelTab', 'enzyme', modifier.id);
      }
    },
    viewReaction: function viewReaction(id) {
      EventBus.$emit('updateSelTab', 'reaction', id);
    },
    displayCompartment(r) {
      const comp = {};
      for (const el of r.reactants) {
        comp[el.compartment] = null;
      }
      for (const el of r.products) {
        comp[el.compartment] = null;
      }
      if (Object.keys(comp).length === 1) {
        return Object.keys(comp)[0];
      } else if (Object.keys(comp).length === 2) {
        return Object.keys(comp).join(' &#8680; ');
      }
      // not possible?
      return '';
    },
    sortBy(field) {
      const reactions = Array.prototype.slice.call(
      this.sortedReactions); // Do not mutate original elms;
      this.sortedReactions = reactions.sort(
        compare(field, this.sortAsc ? 'asc' : 'desc'));
      this.sortAsc = !this.sortAsc;
    },
  },
  beforeMount() {
    $('body').on('click', 'td rc', function f() {
      EventBus.$emit('updateSelTab', 'metabolite', $(this).attr('id'));
    });
  },
};

</script>

<style lang="scss">

.reaction-table {

  rc {
    color: #64CC9A;
  }

  th, rc, span.sc {
    cursor: pointer;
  }

  span.sc {
    border-radius: 10px;
    background: lightgray;
    padding-right: 4px;
    padding-left: 3px;
  }
}

</style>
