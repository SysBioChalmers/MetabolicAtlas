<template>
  <div id="compartment-panel">
    <p class="menu-label">Compartment:</p>
    <ul class="menu-list">
      <li class="m-li" v-for="comp in compartments"
      @click="showCompartment(comp.compartmentID)">
        {{ comp.name }}
      </li>
    </ul>
  </div>
</template>

<script>

import { getCompartments } from '../../helpers/compartment';
import { default as EventBus } from '../../event-bus';

export default {
  name: 'compartment',
  data() {
    return {
      compartmentCount: 0,
      compartments: {},
    };
  },
  created() {
    console.log('compartment created');
    this.loadCompartment();
  },
  methods: {
    loadCompartment() {
      this.compartments = this.getCompartments();
      console.log(this.compartments);
    },
    showCompartment(compartmentID) {
      console.log('Emit from compartment');
      EventBus.$emit('showSVGmap', compartmentID, []);
    },
    getCompartments,
  },
};
</script>

<style lang="scss">

#compartment-panel {
  li.m-li {
    cursor: pointer;
  }

  .li-selected {
    color: #64CC9A;
  }
}
</style>
