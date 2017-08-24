<template>
  <div class="container reaction-table">
    <div class="field">
      <span class="tag">
        # Reaction(s): {{ reactions.length }}
      </span>
    </div>
    <table class="table is-bordered is-striped is-narrow" ref="table">
      <thead>
        <tr style="background: #F8F4F4">
          <th class="is-unselectable"
          v-for="f in fields"
            @click="sortBy(f)">{{ f }}
            </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, index) in sortedReactions">
          <td>{{ r.id }}</td>
          <td v-html="reformatChemicalReactionHTML(r.equation, r)"></td>
          <td>
            <a v-for="(m, index) in r.modifiers" v-on:click.prevent="viewEnzyneReactions(m)"
            >{{ index == 0 ? m.short_name : `, ${m.short_name}` }}</a></td>
          <td>{{ r.subsystem.join('; ') }}</td>
          <td v-html="displayCompartment(r)"></td>
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
  props: ['reactions'],
  data() {
    return {
      fields: ['Reaction ID', 'Equation', 'Modifiers', 'Subsystem', 'Compartment'],
      sortedReactions: [],
      sortAsc: true,
    };
  },
  watch: {
    reactions() {
      this.sortedReactions = this.reactions;
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
        EventBus.$emit('updateSelTab', 3, modifier.id);
      }
    },
    displayCompartment(r) {
      console.log(r);
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
      EventBus.$emit('updateSelTab', 4, $(this).attr('id'));
    });
  },
};

</script>

<style lang="scss">

.reaction-table {

  rc {
    color: #64CC9A;
  }

  th, rc, span.tag {
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
