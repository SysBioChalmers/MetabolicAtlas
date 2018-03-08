<template>
  <div id="metabolicNetwork">
    <div class="columns" id="iTopBar">
      <div class="column" id="iLogo">
        <svg-icon width="175" height="40" :glyph="Logo"></svg-icon>
      </div>
      <div class="column has-text-centered" id="iTitle">
        Metabolic Viewer of <span class="has-text-info">{{ model.toUpperCase() }}</span>
      </div>
      <div class="column">
        <button id="iHideBut" class="button is-dark is-pulled-right" @click="hideNetworkGraph()">Close</button>
      </div>
    </div>
    <div class="columns">
      <div class="column is-2 has-text-centered" id="iSwitch">
        <div class="field">
          <label for="dimSwitch" @click="switch3Dimension(false)">2D Maps</label>
          <input id="dimSwitch" type="checkbox" name="dimSwitch"
           class="switch is-large is-rtl" :checked="{'checked' : dim3D}"
           :disabled="activeSwitch ? false : 'disabled'"
           @click="switch3Dimension()">
          <label for="dimSwitch"></label>
          <label for="dimSwitch" @click="switch3Dimension(true)">&nbsp;3D Force</label>
        </div>
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
      <div class="column" id="svgframe">
        <svgmap v-show="!dim3D" @loadedComponent="handleLoadedComponent" @loading="showLoader=true"></svgmap>
        <d3dforce v-if="dim3D" @loadedComponent="handleLoadedComponent" @loading="showLoader=true"></d3dforce>
        <div id="iLoader" class="loading" v-show="showLoader">
          <a class="button is-loading"></a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

// import $ from 'jquery';
import Compartment from 'components/MetabolicNetwork/Compartment';
import Subsystem from 'components/MetabolicNetwork/Subsystem';
import Region from 'components/MetabolicNetwork/Region';
import Svgmap from 'components/MetabolicNetwork/Svgmap';
import D3dforce from 'components/MetabolicNetwork/D3dforce';
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
    D3dforce,
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
      dim3D: false,
      currentDisplay: 'wholemap',
      compartmentCount: 0,
      subsystemCount: 0,
      initialEmit: false,
      showLoader: false,
    };
  },
  computed: {
    activeSwitch() {
      return ['compartment', 'subsystem'].includes(this.currentDisplay) && !this.showLoader;
    },
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
    if (this.currentDisplay === 'wholemap' && !this.initialEmit) {
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
    switch3Dimension(b) {
      if (this.dim3D) {
        this.dim3D = b;
      } else if (this.currentDisplay !== 'wholemap') {
        if (b !== null) {
          this.dim3D = b;
        } else {
          this.dim3D = !this.dim3D;
        }
      }
    },
    handleLoadedComponent(isSuccess, type, componentName, errorMessage) {
      console.log(`${isSuccess} ${type} ${componentName} ${errorMessage}`);
      if (isSuccess) {
        this.currentDisplay = type;
      }
      this.showLoader = false;
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

  #iSwitch {
    * {
      font-size: 1.5rem;
    }
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

  #iLoader {
    z-index: 10;
    position: absolute;
    background: black;
    top: 0;
    left: 0;
    width: 100%;
    height: 90%;
    opacity: 0.8;
    display: table;
    a {
      color: white;
      font-size: 5em;
      font-weight: 1000;
      display: table-cell;
      vertical-align: middle;
      background: black;
      border: 0;
    }
  }

  #svgframe {
    position: relative;
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
