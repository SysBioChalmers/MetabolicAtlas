<template>
  <div id="metabolicNetwork">
    <div class="container">
      <div id="region-level-button" class="has-text-centered">
        <button class="button" 
          @click="levelSelected='compartment'">
          Compartments ({{ compartmentCount }})</button>
        <button class="button"
         @click="levelSelected='subsystem'">
         Subsystems ({{ subsystemCount }})</button>
        <button class="button"
         @click="levelSelected='reporter'">
         Reporter Metabolite</button>
      </div>
    </div>
    <br>
    <div class="columns">
      <div class="column is-2" v-show="!hideSidebar">
        <div class="box" id="list-res">
          <compartment v-show="levelSelected==='compartment'"></compartment>
          <subsystem v-show="levelSelected==='subsystem'"
            @sendSubSysCount="showSubsystemCount"></subsystem>
          <reporter-metabolites v-show="levelSelected==='reporter'"></reporter-metabolites>
        </div>
      </div>
      <div id="svgframe" class="column"
        :class="hideSidebar ? 'is-12' : 'is-10'">
        <button class="button hb"
          :class="!hideSidebar ? 'hidden' : 'visible'"
          @click="hideSidebar=!hideSidebar"></button>
        <svgmap></svgmap>
      </div>
    </div>
  </div>
</template>

<script>

import Compartment from 'components/MetabolicNetwork/Compartment';
import Subsystem from 'components/MetabolicNetwork/Subsystem';
import ReporterMetabolites from 'components/MetabolicNetwork/ReporterMetabolites';
import Svgmap from 'components/MetabolicNetwork/Svgmap';
import { getCompartments } from '../helpers/compartment';

export default {
  name: 'metabolic-network',
  components: {
    Compartment,
    Subsystem,
    ReporterMetabolites,
    Svgmap,
  },
  data() {
    return {
      errorMessage: '',
      levelSelected: 'compartment',
      hideSidebar: false,
      compartmentCount: 0,
      subsystemCount: 0,
    };
  },
  beforeMount() {
    this.compartmentCount = Object.keys(getCompartments(this.getCompartments())).length;
  },
  methods: {
    showSubsystemCount(count) {
      this.subsystemCount = count;
    },
    getCompartments,
  },
};
</script>

<style lang="scss">

#metabolicNetwork {

  #svgframe {
    position: relative;
  }

  #left-bar.hidden {
    width: 0;
  }

  button.hb {
    position: absolute;
    top: 20px;
    left: -60px;
  }

  button.hb.hidden:before{
    content: '<<';
  }

  button.hb.visible:before{
    content: '>>';
  }

  #region-level-button button {
    display: inline-block;
  }

  .li-selected {
    color: #64CC9A;
  }

}

</style>