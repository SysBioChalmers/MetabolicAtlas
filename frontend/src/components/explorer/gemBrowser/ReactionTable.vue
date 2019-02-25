<template>
  <div class="container reaction-table">
    <div class="field">
      <span class="tag is-medium">
        # Reactions: {{ reactions.length }}
      </span>
      <template v-if="transportReactionCount !== 0">
        &nbsp;including&nbsp;
        <span class="tag link is-medium"  @click="sortBy('compartment', '=>', 'desc')">
          {{ transportReactionCount }} transport reactions
        </span>
      </template>
      <span v-show="reactions.length==200" class="tag is-medium is-warning is-pulled-right">
        The number of reactions displayed is limited to 200, some may have been discarded.
      </span>
    </div>
    <table class="table is-bordered is-striped is-narrow is-fullwidth" ref="table">
      <thead>
        <tr class="has-background-white-ter">
          <th class="is-unselectable"
          v-for="f in fields" v-show="showCol(f.name)"
            @click="sortBy(f.name, null, null)" v-html="f.display"></th>
          <th class="is-unselectable">Map</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, index) in sortedReactions">
          <td>
            <router-link :to="{path: `/explore/gem-browser/${model.database_name}/reaction/${r.id}` }">{{ r.id }}</router-link>
          </td>
          <td v-html="reformatChemicalReactionHTML(r)"></td>
          <td>
            <template v-for="(m, index) in r.modifiers">{{ index == 0 ? '' : ', '}}<router-link :to="{ path: `/explore/gem-browser/${model.database_name}/enzyme/${m.id}` }">{{ m.name || m.id }}</router-link>
            </template
          </td>
          <td v-show="showCP">{{ r.cp }}</td>
          <td v-show="showSubsystem">
            <template v-if="r.subsystem">
              <template v-for="(s, index) in r.subsystem.split('; ')">
              {{ index == 0 ? '' : '; '}}<router-link :to="{ path: `/explore/gem-browser/${model.database_name}/subsystem/${idfy(s)}` }">{{ s }}</router-link>
              </template>
            </template>
          </td>
          <td>
            <template v-for="(RP, i) in r.compartment.split(' => ')">
              <template v-if="i != 0">{{ r.is_reversible ? ' &#8660; ' : ' &#8658; ' }}</template>
              <template v-for="(compo, j) in RP.split(' + ')">
                <template v-if="j != 0"> + </template>
                <router-link :to="{ path: `/explore/gem-browser/${model.database_name}/compartment/${idfy(compo)}` }"> {{ compo }}</router-link>
              </template>
            </template>
          </td>
          <td>
            <button class="button" @click="viewReactionOnMap(r.id)">
              <span class="fa fa-eye"></span>
            </button>
          </td>
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
import { reformatCompEqString, idfy } from '../../../helpers/utils';

export default {
  name: 'reaction-table',
  props: ['reactions', 'selectedElmId', 'showSubsystem', 'model'],
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
      reformatCompEqString,
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
    idfy,
    formatChemicalReaction(v, r) { return chemicalReaction(v, r); },
    reformatChemicalReactionHTML(r) {
      // TODO fix me
      if (this.$parent.$parent.$parent.reformatChemicalReactionLink) {
        return this.$parent.$parent.$parent.reformatChemicalReactionLink(r);
      }
      return this.$parent.$parent.$parent.$parent.reformatChemicalReactionLink(r);
    },
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
    viewReactionOnMap(reactionID) {
      EventBus.$emit('viewReactionOnMap', reactionID);
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
