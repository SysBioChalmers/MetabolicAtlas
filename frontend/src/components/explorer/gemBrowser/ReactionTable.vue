<template>
  <div class="container reaction-table">
    <div class="field">
      <span class="tag is-medium">
        # Reactions: {{ reactions.length }}
      </span>
      <span class="tag is-medium" v-if="transportReactionCount === 0">
        # Transport reactions: {{ transportReactionCount }}
      </span>
      <span class="tag link is-medium" v-else @click="sortBy('compartment', '=>', 'desc')">
        # Transport reactions: {{ transportReactionCount }}
      </span>
      <span v-show="reactions.length==200" class="tag is-medium is-warning is-pulled-right">
        {{ $t('tooManyReactionsTable') }}
      </span>
    </div>
    <table class="table is-bordered is-striped is-narrow is-fullwidth" ref="table">
      <thead>
        <tr class="has-background-white-ter">
          <th class="is-unselectable"
          v-for="f in fields" v-show="showCol(f.name)"
            @click="sortBy(f.name, null, null)" v-html="f.display"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, index) in sortedReactions">
          <td>
            <a @click="viewReaction(r.id)">{{ r.id }}</a>
          </td>
          <td v-html="reformatChemicalReactionHTML(r)"></td>
          <td>
            <a v-for="(m, index) in r.modifiers" v-on:click.prevent="viewEnzyneReactions(m)">
              <template v-if="m.name">{{ index == 0 ? m.name : `, ${m.name}` }}</template>
              <template v-else>{{ index == 0 ? m.id : `, ${m.id}` }}</template>
            </a>
          </td>
          <td v-show="showCP">{{ r.cp }}</td>
          <td v-show="showSubsystem">
            <template v-if="r.subsystem">
              <a v-for="(s, index) in r.subsystem.split('; ')" v-on:click.prevent="viewSubsystem(s)"
              >{{ index == 0 ? s : `; ${s}` }}</a>
            </template>
          </td>
          <td>{{ r.is_reversible ? r.compartment.replace('=>', '&#8660;') : r.compartment.replace('=>', '&#8680;') }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import $ from 'jquery';
import { default as EventBus } from '../../../event-bus';
import { default as compare } from '../../../helpers/compare';
import { chemicalReaction } from '../../../helpers/chemical-formatters';

export default {
  name: 'reaction-table',
  props: ['reactions', 'selectedElmId', 'showSubsystem'],
  data() {
    return {
      showCP: false,
      fields: [{
        display: 'Reaction&nbsp;ID',
        name: 'id',
      }, {
        display: 'Equation',
        name: 'equation',
      }, {
        display: 'Enzymes',
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
      if (this.selectedElmId) {
        this.showCP = true;
        for (const reaction of this.reactions) {
          if (reaction.is_reversible) {
            reaction.cp = 'reversible';
          } else {
            const boolC = reaction.id_equation.split('=>')[0].indexOf(this.selectedElmId) !== -1;
            const boolP = reaction.id_equation.split('=>')[1].indexOf(this.selectedElmId) !== -1;
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
      }
      this.sortedReactions = this.reactions;
    },
  },
  computed: {
    transportReactionCount() {
      return this.reactions.filter(r => r.is_transport).length;
    },
  },
  methods: {
    formatChemicalReaction(v, r) { return chemicalReaction(v, r); },
    reformatChemicalReactionHTML(r) {
      // TODO fix me
      if (this.$parent.$parent.$parent.reformatChemicalReactionLink) {
        return this.$parent.$parent.$parent.reformatChemicalReactionLink(r);
      }
      return this.$parent.$parent.$parent.$parent.reformatChemicalReactionLink(r);
    },
    viewEnzyneReactions(modifier) {
      if (modifier) {
        EventBus.$emit('GBnavigateTo', 'enzyme', modifier.id);
      }
    },
    viewReaction(id) { EventBus.$emit('GBnavigateTo', 'reaction', id); },
    viewSubsystem(id) { EventBus.$emit('GBnavigateTo', 'subsystem', id); },
    sortBy(field, pattern, order) {
      const reactions = Array.prototype.slice.call(
      this.sortedReactions); // Do not mutate original elms;
      let sortOrder = order;
      if (!order) {
        sortOrder = this.sortAsc ? 'asc' : 'desc';
      }
      this.sortedReactions = reactions.sort(
        compare(field, pattern, sortOrder));
      this.sortAsc = !this.sortAsc;
    },
    showCol(name) {
      if (name === 'cp' && !this.showCP) {
        return false;
      } else if (name === 'subsystem' && !this.showSubsystem) {
        return false;
      }
      return true;
    },
  },
  updated() {
    if (this.selectedElmId) {
      // when the table is from the selectedElmId page (metabolite)
      // do not color the selectedElmId is the reaction equations
      $('m').css('color', '');
      $(`.${this.selectedElmId}`).addClass('cms');
    }
  },
};

</script>

<style lang="scss">

.reaction-table {

  m {
    color: #006992;
    &.cms {
      color: rgb(54, 54, 54);
      cursor: default;
    }
  }

  th, m, span.sc, .tag.link {
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
