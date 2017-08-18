<template>
  <div>
    <div class="container">
      <div id="region-level-button" class="has-text-centered">
        
        <button class="button">Compartments ({{ compartmentCount }})</button>
        <button class="button">Subsystems ({{ subsystemCount }})</button>
        <button class="button">Reactions</button>
      </div>
    </div>
    <div class="columns">
      <div class="column is-2" v-show="!hideSidebar">
        <div class="box" id="table-res">
          <p class="menu-label">Subsystem:</p>
          <ul class="menu-list">
            <li class="m-li" v-for="system in systemOrder">
              <span v-if="showSubsystem[system]" 
              class="li-selected"
              @click="toggleShowSubSystem(system)"> &#9662; {{ system }}</span>
              <span v-else
              @click="toggleShowSubSystem(system)"
              > &#9656; {{ system }}</span>
              <ul v-show="showSubsystem[system]">
                <li  v-for="subsystem in subsystems[system]">
                  &#9642; {{ subsystem.name }}
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
      <div id="svgframe" class="column"
        :class="hideSidebar ? 'is-12' : 'is-10'">
        <button class="button hb"
          :class="!hideSidebar ? 'hidden' : 'visible'"
          @click="hideSidebar=!hideSidebar"></button>
        <loader v-show="showLoader"></loader>
        <div v-show="!showLoader" id="svgbox">
          <div id="svgMissing" v-show="true">
            The SVG file is not yet available for this compartment
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import Loader from 'components/Loader';
import { getCompartmentCount } from '../helpers/compartment';

export default {
  name: 'subsystem',
  components: {
    Loader,
  },
  data() {
    return {
      errorMessage: '',
      showLoader: true,
      showResults: false,
      subsystems: {},
      showSubsystem: {},
      hideSidebar: false,
      subsystemCount: 0,
      compartmentCount: 0,
      systemOrder: [
        'Amino Acid metabolism',
        'Fatty acid',
        'Carnitine shuttle',
        'Glycosphingolipid biosynthesis/metabolism',
        'Cholesterol biosynthesis',
        'Vitamin metabolism',
        'Other metabolism',
        'Other',
        'Collection of reactions',
      ],
    };
  },
  mounted() {
    this.loadSubsystem();
    this.compartmentCount = getCompartmentCount();
  },
  methods: {
    loadSubsystem() {
      axios.get('subsystems')
        .then((response) => {
          console.log(response);
          const systems = response.data.reduce((subarray, el) => {
            const arr = subarray;
            if (!arr[el.system]) { arr[el.system] = []; }
            arr[el.system].push(el);
            return arr;
          }, {});
          console.log(systems);
          this.subsystems = systems;
          this.subsystemCount = 0;
          for (const k of Object.keys(systems)) {
            this.showSubsystem[k] = false;
            this.subsystemCount += systems[k].length;
          }
        })
        .catch((error) => {
          console.log(error);
          this.loading = false;
          switch (error.response.status) {
            default:
              this.errorMessage = this.$t('unknownError');
          }
        });
    },
    toggleShowSubSystem(system) {
      const newShowSubsystem = {};
      for (const k of Object.keys(this.subsystems)) {
        newShowSubsystem[k] = false;
      }

      if (!this.showSubsystem[system]) {
        newShowSubsystem[system] = true;
      }
      this.showSubsystem = newShowSubsystem;
    },
    getCompartmentCount,
  },
};
</script>

<style lang="scss">

#svgframe {
  position: relative;
}

#left-bar.hidden {
  width: 0;
}

li.m-li {
  cursor: pointer;
  td {
      padding: 0.3em 0.5em;
  }
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
