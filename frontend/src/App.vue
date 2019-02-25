<template>
  <div id="app">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
    <nav id="navbar" class="navbar has-background-primary-lighter" role="navigation" aria-label="main navigation">
      <div class="container">
        <div class="navbar-brand">
          <router-link id="logo" class="navbar-item" to="/" >
            <img :src="require('./assets/logo.png')"/>
          </router-link>
          <div class="navbar-burger" :class="{ 'is-active': isMobileMenu }"
            @click="isMobileMenu = !isMobileMenu">
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </div>
        </div>
        <div id="#nav-menu" class="navbar-menu" :class="{ 'is-active': isMobileMenu }">
          <div class="navbar-start has-text-centered" v-show="model">
            <router-link v-if="activeViewerBut || activeBrowserBut" :to="{ path: '/explore'}" class="navbar-item is-size-3 has-text-primary has-text-weight-bold is-unselectable"
              title="Current selected model, click to change your selection">{{ model ? model.short_name : '' }}
            </router-link>
            <a class="navbar-item is-unselectable underline" v-if="activeViewerBut || activeBrowserBut"
              :class="{ 'is-active': activeBrowserBut }" @click="goToGemBrowser()">
                GEM Browser
            </a>
            <a class="navbar-item is-unselectable underline" v-if="activeViewerBut || activeBrowserBut"
              :class="{ 'is-active': activeViewerBut }" @click="goToMapViewer()">
                Map Viewer
            </a>
          </div>
          <div class="navbar-end has-background-primary-lighter">
            <template v-for="(menuPath, menuName) in menuElems">
              <template v-if="typeof menuPath === 'string'">
                <router-link class="navbar-item is-unselectable underline"  :to="{ path: menuPath }"
                  :class="{ 'is-active': isActiveRoute(menuPath) }" v-html="menuName">
                </router-link>
              </template>
              <template v-else>
                <template v-for="(submenus, menuurl) in menuPath">
                  <div class="navbar-item has-dropdown is-hoverable is-unselectable has-background-primary-lighter">
                    <a class="navbar-link underline" :class="{ 'is-active': isActiveRoute(menuurl) }"> {{ menuName }} </a>
                    <div class="navbar-dropdown has-background-primary-lighter">
                      <template v-for="submenu in submenus">
                        <template v-for="(submenuPath, submenuName) in submenu">
                          <router-link class="navbar-item is-unselectable has-background-primary-lighter" :to="{ path: submenuPath }" :class="{ 'is-active': isActiveRoute(submenuPath) }" v-html="submenuName">
                          </router-link>
                        </template>
                      </template>
                    </div>
                  </div>
                </template>
              </template>
            </template>
          </div>
        </div>
      </div>
    </nav>
    <keep-alive>
      <router-view></router-view>
    </keep-alive>
    <footer id="footer" class="footer has-background-primary-lighter is-size-6">
      <div class="columns is-gapless">
        <div class="column is-7">
          <p><a href="http://sysbio.se" target="blank">Sys<sup>2</sup>Bio</a> | Department of Biology and Biological Engineering | Chalmers University of Technology</p>
        </div>
        <div class="column">
          <div class="content has-text-right">
            <p>
              <a href="https://www.sysbio.se" title="SysBio">
                <img src="./assets/sysbio-logo.png" />
              </a>
              <a href="http://www.chalmers.se" title="Chalmers University of Technology">
                <img src="./assets/chalmers.png" />
              </a>
              <a href="https://kaw.wallenberg.org/" title="Knut and Alice Wallenberg Foundation">
                <img src="./assets/wallenberg.gif" />
              </a>
              <a href="https://www.kth.se/en/bio/centres/wcpr" title="CBH | KTH Royal Institute of Technology">
                <img src="./assets/wpcr.jpg" />
              </a>
              <a href="https://nbis.se/">
                <img src="./assets/nbislogo-green.png" title="National Bioinformatics Infrastructure Sweden"/>
              </a>
              <a href="https://www.scilifelab.se" title="Science for Life Laboratory (SciLifeLab)">
                <img src="./assets/scilifelab-green.png" />
              </a>
            </p>
          </div>
        </div>
      </div>
    </footer>
    <div v-if="showCookieMsg" id="cookies" class="has-background-grey">
      <div class="column has-text-centered">
        <div class="has-text-white">
          We use cookies to enhance the usability of our website. <a class="has-text-white has-text-weight-semibold" href='/documentation#privacy' target='_blank'>More information</a>
          <p class="button is-small is-rounded has-background-danger has-text-white has-text-weight-bold" @click="showCookieMsg=false; acceptCookiePolicy()">
            <span class="icon is-small"><i class="fa fa-check"></i></span>
            <span>OKAY</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { default as EventBus } from './event-bus';
import { isCookiePolicyAccepted, acceptCookiePolicy } from './helpers/store';

export default {
  name: 'app',
  data() {
    return {
      /* eslint-disable quote-props */
      menuElems: {
        'Explore models': '/explore',
        'GEMs': {
          '/gems/': [
            { 'List of GEMs': '/gems/list' },
            { 'Compare': '/gems/compare' },
            { 'Download': '/gems/download' },
          ],
        },
        'Resources': '/resources',
        'Documentation': '/documentation',
        'About': '/about',
      },
      activeBrowserBut: false,
      activeViewerBut: false,
      showCookieMsg: !isCookiePolicyAccepted(),
      acceptCookiePolicy,
      activeDropMenu: '',
      model: null,
      browserLastPath: '',
      viewerLastPath: '',
      isMobileMenu: false,
    };
  },
  watch: {
    $route: function watchSetup() {
      this.setupButons();
    },
  },
  beforeMount() {
    EventBus.$on('modelSelected', (model) => {
      this.model = model;
      this.viewerLastPath = '';
      this.browserLastPath = '';
    });
  },
  created() {
    this.setupButons();
  },
  methods: {
    setupButons() {
      if (this.$route.name === 'browser' || this.$route.name === 'browserRoot') {
        this.activeBrowserBut = true;
        this.activeViewerBut = false;
        this.savePath();
      } else if (this.$route.name === 'viewer' ||
        this.$route.name === 'viewerCompartment' ||
        this.$route.name === 'viewerSubsystem') {
        this.activeBrowserBut = false;
        this.activeViewerBut = true;
        this.savePath();
      } else {
        this.activeBrowserBut = false;
        this.activeViewerBut = false;
      }
    },
    isActiveRoute(name) {
      if (this.$route.path) {
        return this.$route.path.toLowerCase().includes(name);
      }
      return false;
    },
    goToGemBrowser() {
      this.$router.push(this.browserLastPath || `/explore/gem-browser/${this.$route.params.model}`);
    },
    savePath() {
      if (this.$route.name === 'browser') {
        this.browserLastPath = this.$route.path;
      } else if (this.$route.name === 'browserRoot') {
        this.browserLastPath = '';
      } else if (this.$route.name === 'viewerCompartment' || this.$route.name === 'viewerSubsystem') {
        this.viewerLastPath = this.$route.path;
      } else if (this.$route.name === 'viewer') {
        this.viewerLastPath = '';
      }
    },
    goToMapViewer() {
      this.$router.push(this.viewerLastPath || `/explore/map-viewer/${this.$route.params.model}`);
    },
  },
};
</script>

<style lang='scss'>

$primary: #25543C;
$primary-light: #4C735F;
$primary-lighter: #EEF0EF;
$link: #006992;
$warning: #FFC67D;
$danger: #F46036;
$info: #00549E;

$body-size: 14px !default

$desktop: 1192px !default;
$widescreen: 1384px !default;
$fullhd: 1576px !default;


/* @import "./sass/extensions/_all" FIX ME */
@import '~bulma';
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

.extended-section {
  flex: 1;
}

.has-background-primary-lighter {
  background-color: $primary-lighter;
}

#app {
  display: flex;
  min-height: 100vh;
  flex-direction: column
}

#metabolicViewer {
  background: whitesmoke;
  overflow: hidden;
}

.has-addons {
  .button {
    width: 8rem;
  }
}

#navbar {
  a {
    font-size: 1.15em;
    color: $black-ter;
  }
  a:hover{
    color: $black-bis;
    background-color: $light;
  }
  .is-active {
    color: $black-bis;
    background-color: $grey-lighter;
  }
  .underline.is-active {
    border-bottom: 1px solid $primary;
  }
  .navbar-brand {
    a {
      font-weight: 400;
    }
  }
  .navbar-burger{
    height: 4rem;
    margin-right: 1.5rem;
    width: 5rem;
    padding-left: auto;
    padding-right: auto;
    span {
      height: 2px;
    }
  }
  .navbar-item img {
    max-height: 3rem;
  }
  .navbar-link:not(.is-arrowless)::after {
    border-color: $grey-darker;
  }
}

.footer {
  padding-bottom: 1em;
  padding-top: 1em;
  img {
    max-height: 20px;
    margin: 0 0.5rem;
  }
  sup {
    vertical-align: top;
  }
}

#HPARNAexpLegend {
  margin: auto;
  border-radius: 0;
  .title {
    margin-bottom: 0.3em;
  }

  list-style: none;
  li {
    line-height: 15px;
    display: inline-block;
    &:first-child {
      margin-left: 0;
    }
    span {
      float: left;
      margin: 0;
    }
  }

  span {
    height: 15px;
    &.boxc {
      margin: 0 7px;
      width: 15px;
      border: 1px solid black;
    }
  }

  .exp-lvl-legend {
    list-style: none;
    li {
      span {
        float: left;
        margin: 0;
        width: 1px;
        border: 0
      }
    }
  }
}

#home {
  .menu-list li {

    &:first-child {
      margin-top: 0.75em;
    }
    &:last-child {
      margin-bottom: 0.75em;
    }
    a {
      color: $white-bis;
      padding-left: 1.5em;
    }
    a:hover {
      color: $white-bis;
      background-color: $primary-light;
      border-radius: 0;
    }
    .is-active {
      color: $black;
      background-color: $white;
      border-radius: 0;
    }
  }
  .margin-fix {
    margin-top: 1rem;
    margin-bottom: 1rem;
    margin-left: 0;
  }
  .homepage-submenu {
    margin-left: 2em;
  }
  .more-padding {
    @media only screen and (min-width: $desktop) {
      padding: 3rem 3.75rem 3rem 3.75rem;
    }
  }
  .card-header > .card-content {
    padding-top: 0.5em;
    padding-bottom: 0.5em;
  }
  .is-v-aligned {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  #mobileMenu {
    margin-right: 0;
  }
  #newsandcommunity {
    .card {
      height: 100%;
    }
  }
}

#cookies {
  position: sticky;
  bottom: 0;
  .button:not(:hover) {
    border-color: transparent;
  }
}

#mapViewer {
  #menu {
    width: auto;
    background: $primary;
    color: $white;
    position: relative;
    font-size: 16px;
    ul {
      list-style: none;
      &.vhs, &.l2 {
        max-height: 65vh;
        overflow-y: auto;
      }
    }

    ul.l1, ul.l2 {
      display: none;
      border-left: 1px solid white;
      position: absolute;
      top: 0;
      left: 100%;
      width: 100%;
      background: $primary;
      z-index: 11;
      box-shadow: 5px 5px 5px #222222;
    }

    li {
      padding: 17px 15px 17px 20px;
      border-bottom: 1px solid $grey-lighter;
      user-select: none;
      &:hover {
        background: $primary-light;
      }
      span {
        position: absolute;
        right: 10px;
      }
      &.clickable {
        cursor: pointer;
        &.disable {
          cursor: not-allowed;
          background: $primary;
          color: $grey;
          pointer-events: none;
        }
      }
    }
  }
}

</style>
