<template>
  <div id="metabolicNetwork">
    <div class="columns" id="iTopBar">
      <div class="column" id="iLogo">
        <svg-icon width="175" height="40" :glyph="Logo"></svg-icon>
      </div>
      <div class="column has-text-centered" id="iTitle">
        Metabolic Map
      </div>
      <div class="column">
        <button id="iHideBut" class="button is-info is-pulled-right" @click="hideNetworkGraph()">HIDE</button>
      </div>
    </div>
    <div class="columns">
      <div class="column is-1 has-text-centered" id="iModel">
        Model: {{ model }}
      </div>
      <div class="column is-1">
      </div>
      <div class="column" id="iBarInfo" v-html="mapInfoString">
      </div>
    </div>
     <div class="columns" style="height: auto-height">
      <div class="column is-2" id="iSideBar">
        <section class="accordions">
          <article class="accordion"
          :class="{ 'is-active' : levelSelected === 'search' }"
          >
            <div class="accordion-header toggle"
            :class="{ 'toggle' : levelSelected === 'search' }"
             @click="levelSelected = 'search'">
              <p>Search <i class="fa fa-search"></i></p>
            </div>
            <div class="accordion-body">
              <div class="accordion-content">
                <region :model="model"></region>
              </div>
            </div>
          </article>
          <article class="accordion"
          :class="{ 'is-active' : levelSelected === 'compartment' }"
          >
            <div class="accordion-header"
              :class="{ 'toggle' : levelSelected === 'compartment' }"
              @click="levelSelected = 'compartment'">
              <p>Compartments</p>
              <button class="toggle" aria-label="toggle"></button>
            </div>
            <div class="accordion-body" id="iSearch">
              <div class="accordion-content">
                <compartment :model="model" @showMapInfo="updateMapInfo"></compartment>
              </div>
            </div>
          </article>
          <article class="accordion"
          :class="{ 'is-active' : !['compartment', 'search'].includes(levelSelected) }"
          >
            <div class="accordion-header"
              :class="{ 'toggle' : !['compartment', 'search'].includes(levelSelected) }"
              @click="levelSelected = 'subsystem'">
              <p>Subsystems ({{ subsystemCount }})</p>
              <button class="toggle" aria-label="toggle"></button>
            </div>
            <div class="accordion-body">
              <div class="accordion-content">
                <subsystem :model="model" @sendSubSysCount="showSubsystemCount" ></subsystem>
              </div>
            </div>
          </article>
        </section>
      </div>
      <div class="column" id="svgframe" >
        <svgmap></svgmap>
      </div>
    </div>
    <br>
  </div>
</template>

<script>

// import $ from 'jquery';
import Compartment from 'components/MetabolicNetwork/Compartment';
import Subsystem from 'components/MetabolicNetwork/Subsystem';
import Region from 'components/MetabolicNetwork/Region';
import Svgmap from 'components/MetabolicNetwork/Svgmap';
import SvgIcon from 'components/SvgIcon';
import bulmaAccordion from 'bulma-extensions/bulma-accordion/dist/bulma-accordion.min';
import Logo from '../assets/logo.svg';
import { default as EventBus } from '../event-bus';
import { getCompartments } from '../helpers/compartment';


export default {
  name: 'metabolic-network',
  components: {
    SvgIcon,
    Compartment,
    Subsystem,
    Region,
    Svgmap,
  },
  props: [
    'model',
  ],
  data() {
    return {
      Logo,
      errorMessage: '',
      mapInfoString: '',
      levelSelected: 'subsystem',
      selectedModel: 'hmr2',
      // hideSidebar: false,
      compartmentCount: 0,
      subsystemCount: 0,
      initialEmit: false,
    };
  },

  beforeMount() {
    this.compartmentCount = Object.keys(getCompartments(this.getCompartments())).length;
  },
  mounted() {
    this.view = this.$route.query.view;
    if (!this.view) {
      // load subsystem view
      this.levelSelected = 'subsystem';
    }
    console.log(this.$route.query);
    if (this.$route.query.tab && this.$route.query.tab === '1' && !this.initialEmit) {
      console.log('initial emit whole map');
      EventBus.$emit('showSVGmap', 'wholemap', null, []);
      this.initialEmit = true;
    }
  },
  methods: {
    showSubsystemCount(count) {
      this.subsystemCount = count;
    },
    updateMapInfo(text) {
      this.mapInfoString = text;
    },
    hideNetworkGraph() {
      EventBus.$emit('toggleNetworkGraph');
    },
    getCompartments,
    bulmaAccordion,
  },
};
</script>

<style lang="scss">

#metabolicNetwork {

  #iTopBar {
    border-bottom: 1px solid black;
    .column {
      padding-bottom: 0;
    }
  }

  #iLogo {
    margin-top: 5px;
  }

  #iTitle {
    font-size: 2em;
    font-style: bold;
  }

  #iHideBut {
    margin: 10px;
  }

  #iModel {
    font-size: 1.2em;
  }

  #iBarInfo {
    background: teal;
    color: white;
    font-style: bold;
    font-size: 1.1em;
  }

  #iSideBar {
    padding: 0;
    margin: 0;
    height: 100%;
    /* background: red; */
  }

  #accordion {
    > h3 {
      font-size: 1.5em;
      border: 1px solid black;
      cursor: pointer;
      padding-left: 1em;
      margin-bottom: 2px;
      background: lightgray;
    }

    > div {
      padding: 20px;
    }
  }

  #iSearch {
    bottom: 0;
  }

  #svgframe {
    width: 100%;
    height: 100vh;
    padding: 0;
    margin: 0;
    border: 1px solid darkgray;
    /* background: green; */
  }

  #left-bar.hidden {
    width: 0;
  }

  #region-level-button button {
    display: inline-block;
  }

  .li-selected {
    color: #64CC9A;
  }

}

</style>
