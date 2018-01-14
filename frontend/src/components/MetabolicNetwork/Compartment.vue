<template>
  <div>
    <div id="compartment-panel">
      <p class="menu-label">Compartment:</p>
      <ul class="menu-list">
        <li class="m-li" v-for="comp in compartments"
        :class="{ 'selected' : selectedCompartmentID==comp.compartmentID }"
        @click="showCompartment(comp.compartmentID)">
          {{ comp.name}}
        </li>
      </ul>
    </div>
    <div v-if="currentCompartment && compartmentStats">
      <hr>
      <table class="table is-narrow is-fullwidth">
        <tbody>
          <tr>
            <td># Metabolites</td><td>{{ currentCompartment.nr_metabolites }}</td>
          </tr>
          <tr>
            <td># Enzymes</td><td>{{ currentCompartment.nr_enzymes }}</td>
          </tr>
          <tr>
            <td># Reactions</td><td>{{ currentCompartment.nr_reactions  }}</td>
          </tr>
          <tr>
            <td># Subsystems</td><td>{{ currentCompartment.nr_subsystems  }}</td>
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
  props: ['model'],
  data() {
    return {
      compartments: [],
      compartmentStats: {},
      currentCompartment: null,
      selectedCompartmentID: 0,
      // compartmentIDOrder2: [6, 7, 5, 3, 8, 2, 20, 21, 22, 23, 24, 25],
      compartmentIDOrder: [4, 5, 3, 2, 6, 1, 7, 8, 9, 10, 11, 12],
    };
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
      for (const CID of this.compartmentIDOrder) {
        this.compartments.push(getCompartmentFromCID(CID));
      }
      axios.get(`${this.model}/compartment_information/`)
      .then((response) => {
        // console.log(response);
        this.compartmentStats = {};
        for (const compInfo of response.data) {
          this.compartmentStats[compInfo.id] = compInfo;
        }
        this.currentCompartment = this.compartmentStats[0];
      })
      .catch((error) => {
        console.log(error);
      });
    },
    showCompartment(compartmentID) {
      this.selectedCompartmentID = compartmentID;
      this.currentCompartment = this.compartmentStats[compartmentID];
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
