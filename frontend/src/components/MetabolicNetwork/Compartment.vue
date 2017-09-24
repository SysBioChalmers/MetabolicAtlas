<template>
  <div>
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
    <div v-show="selectedCompartmentID && selCompartmentStats">
      <hr>
      <table class="table is-narrow is-fullwidth">
        <tbody>
          <tr>
            <td># Metabolite</td><td>{{ selCompartmentStats.metabolite_count }}</td>
          </tr>
          <tr>
            <td># Enzyme</td><td>{{ selCompartmentStats.enzyme_count }}</td>
          </tr>
          <tr>
            <td># Reaction</td><td>{{ selCompartmentStats.reaction_count }}</td>
          </tr>
          <tr>
            <td># Subsystem</td><td>{{ selCompartmentStats.subsystem_count }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import { getCompartmentFromCID } from '../../helpers/compartment';
import { default as EventBus } from '../../event-bus';

export default {
  name: 'compartment',
  data() {
    return {
      compartmentCount: 0,
      compartments: [],
      selectedCompartmentID: 0,
      selCompartmentStats: {},
      compartmentIDOrder: [6, 7, 5, 3, 8, 2, 20, 21, 22, 23, 24, 25],
    };
  },
  beforeMount() {
    this.loadCompartments();
  },
  created() {
    EventBus.$on('showCompartment', (id) => {
      this.showCompartment(id);
    });
    EventBus.$on('resetView', () => {
      this.selectedCompartmentID = 0;
    });
    this.loadCompartments();
  },
  methods: {
    loadCompartments() {
      this.compartments = [];
      for (const CID of this.compartmentIDOrder) {
        this.compartments.push(getCompartmentFromCID(CID));
      }
    },
    loadCompartmentStats(compartmentID) {
      console.log(compartmentID);
      axios.get(`compartment/${compartmentID}`)
        .then((response) => {
          console.log(response);
          this.selCompartmentStats = response.data;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    showCompartment(compartmentID) {
      this.selectedCompartmentID = compartmentID;
      this.loadCompartmentStats(compartmentID);
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
