<template>
  <div id="metabolicViewer">
    <div class="columns" id="iTopBar">
      <div class="column" id="iLogo">
        <svg-icon width="175" height="40" :glyph="Logo"></svg-icon>
      </div>
      <div class="column has-text-centered" id="iTitle">
        Metabolic Viewer of <span class="has-text-info">{{ model.name.toUpperCase() }}</span>
      </div>
      <div class="column">
        <button id="iHideBut" class="button is-dark is-pulled-right" @click="hideNetworkGraph()">Close</button>
      </div>
    </div>
    <div class="columns">
      <div class="column is-2 has-text-centered" id="iSwitch">
        <div class="field">
          <label for="" @click="switch3Dimension(false)">2D Maps</label>
          <input id="dimSwitch" type="checkbox" name="dimSwitch"
           class="switch is-large is-rtl" :checked="!dim3D"
           :disabled="activeSwitch ? false : 'disabled'">
          <label for="" @click="switch3Dimension(null)"></label>
          <label for="" @click="switch3Dimension(true)">&nbsp;3D Force</label>
        </div>
      </div>
      <div class="column" id="iBarInfo" v-html="mapInfoString">
      </div>
    </div>
     <div class="columns" style="height: auto-height">
      <div class="column is-2" id="iSideBar">
        <section class="accordions">
          <article class="accordion"
          :class="{ 'is-active' : accordionLevelSelected === 'search' }"
          >
            <div class="accordion-header toggle"
            :class="{ 'toggle' : accordionLevelSelected === 'search' }"
             @click="accordionLevelSelected = 'search'">
              <p>Search <i class="fa fa-search"></i></p>
            </div>
            <div class="accordion-body">
              <div class="accordion-content">
                <finder :model="model.id"></finder>
              </div>
            </div>
          </article>
          <article class="accordion"
          :class="{ 'is-active' : accordionLevelSelected === 'wholemap' }"
          >
            <div class="accordion-header"
              :class="{ 'toggle' : accordionLevelSelected === 'wholemap' }"
              @click="globalMapSelected">
              <p>Global map</p>
            </div>
            <div class="accordion-body">
            </div>
          </article>
          <article class="accordion"
          :class="{ 'is-active' : accordionLevelSelected === 'compartment' }"
          >
            <div class="accordion-header"
              :class="{ 'toggle' : accordionLevelSelected === 'compartment' }"
              @click="accordionLevelSelected = 'compartment'">
              <p>Compartments</p>
              <button class="toggle" aria-label="toggle"></button>
            </div>
            <div class="accordion-body" id="iSearch">
              <div class="accordion-content">
                <compartment :model="model.id" @showMapInfo="updateMapInfo"
                :compartmentName="currentDisplayedName"></compartment>
              </div>
            </div>
          </article>
          <article class="accordion"
          :class="{ 'is-active' : !['compartment', 'search'].includes(accordionLevelSelected) }"
          >
            <div class="accordion-header"
              :class="{ 'toggle' : !['compartment', 'search'].includes(accordionLevelSelected) }"
              @click="accordionLevelSelected = 'subsystem'">
              <p>Subsystems ({{ subsystemCount }})</p>
              <button class="toggle" aria-label="toggle"></button>
            </div>
            <div class="accordion-body">
              <div class="accordion-content">
                <subsystem :model="model.id" @sendSubSysCount="showSubsystemCount"
                :subsystemName="currentDisplayedName" @showMapInfo="updateMapInfo"></subsystem>
              </div>
            </div>
          </article>
        </section>
      </div>
      <div class="column is-10" id="graphframe">
        <div class="columns">
          <svgmap class="column" v-show="!dim3D"
          :model="model.id"
          @loadedComponent="handleLoadedComponent"
          @loading="showLoader=true"></svgmap>
          <d3dforce class="column" v-show="dim3D"
          :model="model.id"
          @loadedComponent="handleLoadedComponent"
          @loading="showLoader=true"></d3dforce>
        </div>
        <div id="iLoader" class="loading" v-show="showLoader">
          <a class="button is-loading"></a>
        </div>
      </div>
    </div>
    <transition name="slide-fade">
      <article id="errorBar" class="message is-danger" v-if="errorMessage">
        <div class="message-header">
          <i class="fa fa-warning"></i>
        </div>
        <div class="message-body">
          <h5 class="title is-5">{{ errorMessage }}</h5>
        </div>
      </article>
    </transition>
  </div>
</template>

<script>

// import $ from 'jquery';
import bulmaAccordion from 'bulma-extensions/bulma-accordion/dist/bulma-accordion.min';
import Compartment from './metabolicViewerComponents/Compartment';
import Subsystem from './metabolicViewerComponents/Subsystem';
import Finder from './metabolicViewerComponents/Finder';
import Svgmap from './metabolicViewerComponents/Svgmap';
import D3dforce from './metabolicViewerComponents/D3dforce';
import SvgIcon from './SvgIcon';
import Logo from '../assets/logo.svg';
import { default as EventBus } from '../event-bus';
import { getCompartments } from '../helpers/compartment';


export default {
  name: 'metabolic-viewer',
  components: {
    SvgIcon,
    Compartment,
    Subsystem,
    Finder,
    Svgmap,
    D3dforce,
  },
  props: [
    'model', 'init',
  ],
  data() {
    return {
      Logo,
      errorMessage: '',
      mapInfoString: '',
      accordionLevelSelected: 'subsystem',
      dim3D: false,
      requestedType: '',
      requestedName: '',
      currentDisplayedType: 'wholemap',
      currentDisplayedName: '',
      // compartmentCount: 0,
      subsystemCount: 0,
      initialEmit: false,
      showLoader: false,
    };
  },
  computed: {
    activeSwitch() {
      return ['compartment', 'subsystem'].includes(this.currentDisplayedType) && !this.showLoader;
    },
  },
  created() {
    // this.compartmentCount = Object.keys(getCompartments(this.getCompartments())).length;
    EventBus.$on('showAction', (type, name, secondaryName, ids) => {
      console.log(`showAction ${type} ${name} ${secondaryName} ${ids}`);
      console.log(this.dim3D);
      this.requestedType = type;
      if (type === 'subsystem') {
        this.requestedName = secondaryName;
      } else {
        this.requestedName = name;
      }
      if (this.dim3D) {
        if (['compartment', 'subsystem'].includes(type)) {
          EventBus.$emit('show3Dnetwork', type, this.requestedName);
        } else {
          // show error
        }
      } else {
        EventBus.$emit('showSVGmap', type, name, ids);
      }
    });
  },
  mounted() {
    if (false && this.currentDisplayedType === 'wholemap' &&
     !this.initialEmit) {
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
    globalMapSelected() {
      this.accordionLevelSelected = 'wholemap';
      this.switch3Dimension(false);
      EventBus.$emit('showSVGmap', 'wholemap', null, []);
    },
    switch3Dimension(b) {
      if (!this.activeSwitch) {
        return;
      }
      if (this.dim3D) {
        this.dim3D = b;
      } else if (this.currentDisplayedType !== 'wholemap') {
        if (b !== null) {
          this.dim3D = b;
        } else {
          this.dim3D = !this.dim3D;
        }
      }
      if (this.dim3D) {
        EventBus.$emit('show3Dnetwork', this.currentDisplayedType, this.currentDisplayedName);
      } else {
        EventBus.$emit('destroy3Dnetwork');
        EventBus.$emit('showSVGmap', this.currentDisplayedType, this.currentDisplayedName, []);
      }
    },
    handleLoadedComponent(isSuccess, errorMessage) {
      console.log(`${isSuccess} ${errorMessage}`);
      if (!isSuccess) {
        // show error
        this.errorMessage = errorMessage;
        this.showLoader = false;
        setTimeout(() => {
          this.errorMessage = '';
        }, 3000);
        return;
      }
      this.currentDisplayedType = this.requestedType;
      this.currentDisplayedName = this.requestedName;
      this.showLoader = false;
    },
    getCompartments,
    bulmaAccordion,
  },
};
</script>

<style lang="scss">

#metabolicViewer {
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
    label {
      font-size: 1.5rem;
      cursor: pointer;
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

  #graphframe {
    position: relative;
    height: 100vh;
    padding: 0;
    margin: 0;
    border: 1px solid darkgray;
  }

  #errorBar {
    position: absolute;
    margin: 0;
    right: 0;
    bottom: 0;
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

  .slide-fade-enter-active {
    transition: all .3s ease;
  }
  .slide-fade-leave-active {
    transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0);
  }
  .slide-fade-enter, .slide-fade-leave-active {
    transform: translateX(200px);
    opacity: 0;
  }

}

</style>
