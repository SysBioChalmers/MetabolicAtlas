<template>
  <div id="compartment-panel">
    <p class="menu-label">Compartment:</p>
    <ul class="menu-list">
      <li class="m-li" v-for="comp in compartments"
      :class="{ 'selected' : selectedCompartmentID==comp.compartmentID }"
      @click="showCompartment(comp.compartmentID)">
        {{ comp.name }}
      </li>
    </ul>
  </div>
</template>

<script>

import { getCompartmentFromCID } from '../../helpers/compartment';
import { default as EventBus } from '../../event-bus';

export default {
  name: 'compartment',
  data() {
    return {
      compartmentCount: 0,
      compartments: [],
      selectedCompartmentID: 0,
      // compartmentIDOrder: [6, 7, 5, 3, 8, 2, 20, 21, 22, 23, 24, 25],
      compartmentIDOrder: [6, 7, 5, 3, 8, 2],
    };
  },
  beforeMount() {
    this.loadCompartment();
  },
  created() {
    console.log('compartment created');
    EventBus.$on('showCompartment', (id) => {
      this.selectedCompartmentID = id;
      this.showCompartment(id);
    });
    EventBus.$on('resetView', () => {
      this.selectedCompartmentID = 0;
    });
    this.loadCompartment();
  },
  methods: {
    loadCompartment() {
      this.compartments = [];
      for (const CID of this.compartmentIDOrder) {
        this.compartments.push(getCompartmentFromCID(CID));
      }
    },
    showCompartment(compartmentID) {
      this.selectedCompartmentID = compartmentID;
      EventBus.$emit('showSVGmap', 'compartment', compartmentID, []);
    },
    getCompartmentFromCID,
  },
};
</script>

<style lang="scss">

#compartment-panel {
  li.m-li {
    cursor: pointer;
  }

  .m-li.selected {
    color: #64CC9A;
  }
}
</style>
