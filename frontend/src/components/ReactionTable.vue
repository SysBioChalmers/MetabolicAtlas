<template>
  <div class="container reaction-table">
    <table class="table is-bordered is-striped is-narrow" ref="table">
      <thead>
        <tr>
          <th>Reaction Id</th>
          <th>Equation</th>
          <th v-if="false">Reactants</th>
          <th v-if="false">Products</th>
          <th>Modifiers</th>
          <th>Sub-system</th>
          <th>Compartment</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in reactions">
          <td>{{ r.id }}</td>
          <td v-html="formatChemicalReaction(r.equation)"></td>
          <td v-if="false">{{ r.reactants.length }}</td>
          <td v-if="false">{{ r.products.length }}</td>
          <td>
            <span 
            class="tag is-primary is-medium"
            v-on:click.prevent="viewEnzyneReactions(m)"
            v-for="m in r.modifiers">
            {{ m.short_name }}</span>
          </td>
          <td>{{ r.subsystem }}</td>
          <td>{{ r.modifiers.length !== 0 ? r.modifiers[0].compartment : '' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { default as EventBus } from '../event-bus';
import { chemicalReaction } from '../helpers/chemical-formatters';

export default {
  name: 'reaction-table',
  props: ['reactions'],
  methods: {
    formatChemicalReaction(v) {
      return chemicalReaction(v);
    },
    viewEnzyneReactions: function viewEnzyneReactions(modifier) {
      if (modifier) {
        EventBus.$emit('updateSelTab', 3, modifier.id);
      }
    },
  },
};

</script>

<style lang="scss">

span.tag {
  cursor: pointer;

}

</style>
