<template>
  <div id="app" class="hero is-fullheight">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
    <transition name="fade">
      <metabolic-network id="metabolicNetwork" v-show="isShowNetworkGraph" :model="selectedModel"></metabolic-network>
    </transition>
    <div class="hero-head">
      <nav class="navbar" role="navigation" aria-label="main navigation">
        <div class="navbar-brand">
          <a id="logo" class="navbar-item" @click="goToPage('')" >
            <svg-icon width="175" height="75" :glyph="Logo"></svg-icon>
          </a>
          <div class="navbar-burger" data-target="navMenu">
            <span
               v-show="false"
               v-for="menuItem in menuItems"
               :class="[{ 'is-active': isActive(menuItem) }, '']"
               @click="goToPage(menuItem)"
            >{{ menuItem }}</span>
          </div>
        </div>
        <div class="navbar-menu" id="#nav-menu">
          <div class="navbar-end">
            <a class="navbar-item" v-show="!isShowNetworkGraph">
              <div class="button is-info" @click="showNetworkGraph()">Metabolic Map</div>
            </a>
            <a
               v-for="menuItem in menuItems"
               class="navbar-item"
               :class="[{ 'is-active': isActive(menuItem) }, '']"
               @click="goToPage(menuItem)"
            >{{ menuItem }}</a>
          </div>
        </div>
      </nav>
    </div>
    <div class="hero-body">
      <div class="container">
        <router-view></router-view>
      </div>
    </div>
    <div class="hero-foot">
      <footer class="footer">
        <div class="container">
          <div class="content has-text-centered">
            <p v-html="$t('footerText')"><p>
            <p>
              <a href="http://www.chalmers.se"><img src="./assets/chalmers.png" /></a>
              <a href="https://kaw.wallenberg.org/"><img src="./assets/wallenberg.gif" /></a>
              <a href="https://www.kth.se/en/bio/centres/wcpr"><img src="./assets/wpcr.jpg" /></a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>

import SvgIcon from './components/SvgIcon';
import MetabolicNetwork from './components/MetabolicNetwork';
import Logo from './assets/logo.svg';
import router from './router';
import { default as EventBus } from './event-bus';


export default {
  name: 'app',
  components: {
    SvgIcon,
    MetabolicNetwork,
  },
  data() {
    return {
      Logo,
      menuItems: [
        this.$t('navBut1Title'),
        this.$t('navBut2Title'),
        this.$t('navBut3Title'),
        this.$t('navBut4Title'),
        this.$t('navBut5Title'),
        this.$t('navBut6Title'),
        this.$t('navBut7Title'),
      ],
      isShowNetworkGraph: false,
      selectedModel: 'hmr2',
    };
  },
  created() {
    EventBus.$on('requestViewer', (type, name, secondaryName, ids) => {
      this.isShowNetworkGraph = true;
      console.log(`requestViewer ${type}, ${name}, ${secondaryName}, ${ids}`);
      EventBus.$emit('showAction', type, name, secondaryName, ids);
    });
    EventBus.$on('toggleNetworkGraph', () => {
      this.isShowNetworkGraph = !this.isShowNetworkGraph;
    });
    EventBus.$on('updateSelectedModel', (model) => {
      this.selectedModel = model;
    });
  },
  methods: {
    goToPage(name) {
      // TODO: make this not hard-coded
      if (name === this.menuItems[0]) {
        router.push(
          {
            path: '/',
            query: {
              tab: 1,
            },
          },
        );
      } else if (['tools', 'databases'].includes(name.toLowerCase())) {
        router.push(`Resources#${name.toLowerCase()}`);
      } else {
        router.push(`/${name}`);
      }
    },
    isActive(name) {
      if (this.$route.name) {
        return name.toLowerCase() === this.$route.name.toLowerCase();
      }
      return false;
    },
    showNetworkGraph() {
      EventBus.$emit('toggleNetworkGraph');
    },
  },
};
</script>

<style lang='scss'>

$primary: #64CC9A;
$link: #64CC9A;
$warning: #FFC67D;
$danger: #FF865C;

$body-size: 14px !default

$desktop: 1192px !default;
$widescreen: 1384px !default;
$fullhd: 1576px !default;
$switch-background: $primary;


/* @import "./sass/extensions/_all" FIX ME */
@import '~bulma';
@import '~bulma-extensions/bulma-accordion/dist/bulma-accordion';
@import '~bulma-extensions/bulma-switch/dist/bulma-switch';
@import './styles/mixins';

@include keyframes(rotating) {
  0% {
    transform: rotate(0deg);
    transform-origin: center center;
  }
  100% {
    transform: rotate(360deg);
    transform-origin: center center;
  }
}

#metabolicNetwork {
  position: fixed;
  z-index:100;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100%;
  width: 100%;
  background: whitesmoke;
  overflow: hidden;
}

.navbar-menu {
  a {
    font-size: 1.15em;
  }
}

.footer {
  padding-bottom: 2em;
  img {
    max-height: 75px;
  }
  sup {
    vertical-align: top;
  }
}

.hero.is-fullheight .hero-body {
  align-items: initial;
  display: flex;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

</style>
