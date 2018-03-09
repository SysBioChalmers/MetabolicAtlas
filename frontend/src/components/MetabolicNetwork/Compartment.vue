<template>
  <div>
    <div id="compartment-panel">
      <ul class="menu-list">
        <li class="m-li" v-for="comp in compartments"
        :class="{ 'selected' : compartmentName==comp.name }"
        @click="showCompartment(comp.name)">
          {{ comp.name }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import { getCompartmentFromName } from '../../helpers/compartment';
import { default as EventBus } from '../../event-bus';

export default {
  name: 'compartment',
  props: ['model', 'compartmentName'],
  data() {
    return {
      compartments: [],
      compartmentStats: {},
      currentCompartment: null,
      compartmentNameOrder: [
        'Endoplasmic reticulum',
        'Golgi apparatus',
        'Lysosome',
        'Mitochondria',
        'Nucleus',
        'Peroxisome',
        'Cytosol_1',
        'Cytosol_2',
        'Cytosol_3',
        'Cytosol_4',
        'Cytosol_5',
        'Cytosol_6',
      ],
    };
  },
  watch: {
    compartmentName(newVal, oldVal) { // eslint-disable-line no-unused-vars
      if (this.compartmentName in this.compartmentStats) {
        this.currentCompartment = this.compartmentStats[this.compartmentName];
        const s = `${this.currentCompartment.display_name} - ${this.currentCompartment.nr_metabolites} Metabolites; ${this.currentCompartment.nr_enzymes} Enzymes; ${this.currentCompartment.nr_reactions} Reactions; ${this.currentCompartment.nr_subsystems} Subsystems`;
        this.$emit('showMapInfo', s);
      }
    },
  },
  created() {
    EventBus.$on('showCompartment', (id) => {
      this.showCompartment(id);
    });
    this.loadCompartments();
  },
  methods: {
    loadCompartments() {
      for (const Cname of this.compartmentNameOrder) {
        this.compartments.push(getCompartmentFromName(Cname));
      }
      axios.get(`${this.model}/compartment_information/`)
      .then((response) => {
        this.compartmentStats = {};
        for (const compInfo of response.data) {
          this.compartmentStats[compInfo.display_name] = compInfo;
        }
        this.currentCompartment = null;
      })
      .catch((error) => {
        console.log(error);
      });
    },
    showCompartment(compartmentName) {
      EventBus.$emit('requestViewer', 'compartment', compartmentName, '', []);
    },
    getCompartmentFromName,
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
