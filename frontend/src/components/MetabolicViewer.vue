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
    </div> -->
     <div class="columns" style="height: auto-height">
      <div class="column is-one-fifth" id="iSideBar">
        <div id="menu">
          <ul class="l0">
            <li>HPA RNA levels
            </li>
          </ul>
          <ul class="l0">
            <li>Compartments<span>&nbsp;&#9656;</span>
              <ul class="l1">
                <li v-for="comp in compartments" class="clickable"
                @click="showCompartment(comp.name)">
                  {{ comp.name }}
<!--                    TODO ADD subystem for cytosol parts
 -->                </li>
              </ul>
            </li>
          </ul>
          <ul class="l0">
            <li>Subsystems<span>&nbsp;&#9656;</span>
              <ul class="l1">
                <li v-for="system in systemOrder">{{ system }}<span>&nbsp;&#9656;</span>
                  <ul class="l2">
                    <li v-for="subsystem in subsystems[system]" class="clickable" 
                      v-if="system !== 'Collection of reactions'">
                        {{ subsystem.name }}
                    </li>
                    <li v-else class="clickable disable">
                       {{ subsystem.name }}
                    </li>
                  </ul>
                </li>
              </ul>
            </li>
          </ul>
        </div>
        <div class="column">
          <div id="iSelectedDataFrame">
          </div>
        </div>
      </div>
      <div class="column" id="graphframe">
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
import axios from 'axios';
// TODO remove bulm accordion fron package
import Svgmap from './metabolicViewerComponents/Svgmap';
import D3dforce from './metabolicViewerComponents/D3dforce';
import SvgIcon from './SvgIcon';
import Logo from '../assets/logo.svg';
import { default as EventBus } from '../event-bus';
import { getCompartmentFromName } from '../helpers/compartment';


export default {
  name: 'metabolic-viewer',
  components: {
    SvgIcon,
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
      initialEmit: false,
      showLoader: false,

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
      subsystems: {},
      currentubsystem: null,
      subsystemCount: 0,
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

    this.loadCompartments();

    // subsystem
    /* eslint-disable no-param-reassign */
    EventBus.$on('showSubsystem', (name) => {
      if (!name) {
        const subname = 'Tricarboxylic acid cycle and glyoxylate/dicarboxylate metabolism';
        this.selectedSystem = 'Other metabolism';
        this.selectedSubsystem = this.subsystems[subname];
        this.loadSubsystemCoordinates(subname, null);
      } else {
        this.loadSubsystemCoordinates(name, null);
      }
    });
    this.loadSubsystem();
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
    loadCompartments() {
      for (const Cname of this.compartmentNameOrder) {
        this.compartments.push(getCompartmentFromName(Cname));
      }
      axios.get(`${this.model.id}/compartments_svg/`)
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
    loadSubsystem() {
      axios.get(`${this.model.id}/subsystems`)
        .then((response) => {
          const systems = response.data.reduce((subarray, el) => {
            const arr = subarray;
            if (!arr[el.system]) { arr[el.system] = []; }
            arr[el.system].push(el);
            return arr;
          }, {});
          this.subsystems = systems;
          this.subsystemCount = 0;
          for (const k of Object.keys(systems)) {
            this.subsystems[k] = this.subsystems[k].sort(
              (a, b) => {
                if (a.name > b.name) {
                  return 1;
                }
                return a.name < b.name ? -1 : 0;
              }
            );
            this.subsystemCount += systems[k].length;
          }
        })
        .catch((error) => {
          this.loading = false;
          switch (error.response.status) {
            default:
              this.errorMessage = this.$t('unknownError');
          }
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

/*  #iSwitch {
    label {
      font-size: 1.5rem;
      cursor: pointer;
    }
  }*/

  #iSideBar {
    padding: 0;
    margin: 0;
    height: 100%;
    font-size: 18px;
    /* background: red; */

    #iSelectedDataFrame {
      height: 100%;
      background: #AAAAAA;
      margin-left: 0.75rem;
    }
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
    > .columns {
      margin: 0;
      > .column {
        padding: 0;
      }
    }
  }

  #errorBar {
    position: absolute;
    margin: 0;
    right: 0;
    bottom: 0;
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

  #menu {width: auto; background: #4a4a4a; color: white; position: relative;}
  #menu ul {
    list-style: none;
    .l2 {
      max-height: 75vh;
      overflow-y: auto;
    }
  }
  #menu li {
    padding: 17px 15px 17px 20px;
    border-bottom: 1px solid gray;
    border-left: 1px solid white;
    user-select: none;

    &:hover {
      background: #2a2a2a;
    }
    span {
      position: absolute;
      right: 10px;
    }

    &.clickable {
        cursor: pointer;
        &.disable {
          cursor: default;
          background: #4a4a4a;
          color: gray;
        }
    }

  }
/*  #menu li.disable {
    color: gray;
  }*/
  #menu ul ul {position: absolute; top: 0; left: 100%; width: 100%; background: #4a4a4a; z-index: 11}
  #menu ul ul.l1 {display: none;}
  #menu ul li:hover ul.l1 {display: block;}
  #menu ul li.disable:hover ul.l1 {display: none;}
  #menu ul ul.l2 {display: none;}
  #menu ul.l1 li:hover ul.l2 {display: block;}
  #menu ul.l1 li.disable:hover ul.l2 {display: none;}
}

</style>
