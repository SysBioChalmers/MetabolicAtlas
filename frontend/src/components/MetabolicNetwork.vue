<template>
  <div>
    <div class="container">
      <div id="region-level-button" class="has-text-centered">
        <button class="button">Compartments ({{ compartmentCount }})</button>
        <button class="button">Subsystems ({{ subsystemCount }})</button>
        <button class="button">Reporter Metabolite</button>
      </div>
    </div>
    <div class="columns">
      <div class="column is-2" v-show="!hideSidebar">
        <div class="box" id="list-res">
          <compartment><compartment>
          <subsystem></subsystem>
          <reporter-metabolites ></reporter-metabolites>
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

export default {
  name: 'metabolic-network',
  components: {
    Compartment,
    Subsystem,
    ReporterMetabolites,
  },
  data() {
    return {
      errorMessage: '',
      showResults: false,
      hideSidebar: false,
      compartmentCount: 0,
      subsystemCount: 0,
    };
  },
  methods: {
  },
};
</script>

<style lang="scss" scoped>

#svgframe {
  position: relative;
}

#left-bar.hidden {
  width: 0;
}

button.hb {
  position: absolute;
  top: 30px;
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

</style>