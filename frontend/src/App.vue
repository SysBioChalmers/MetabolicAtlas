<template>
  <div id="app">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
    <nav id="navbar" class="navbar has-background-light" role="navigation" aria-label="main navigation">
      <div class="container">
        <div class="navbar-brand">
          <a id="logo" class="navbar-item" @click="goToPage('')" >
            <svg-icon width="175" height="75" :glyph="Logo"></svg-icon>
          </a>
          <a class="navbar-item" v-if="showExploreInfo"
             :class="{ 'is-active': activeBrowserBut }"
             @click="goToGemsBrowser()">
             GEM<br>Browser
          </a>
          <a class="navbar-item" v-if="showExploreInfo"
             :class="{ 'is-active': activeViewerBut }"
             @click="goToGemsViewer()">
             Map<br>Viewer
          </a>
          <span v-if="showExploreInfo" id="modelHeader" class="is-unselectable" style="margin: auto 0">
            <span class="is-size-3 has-text-primary has-text-weight-bold">{{ $t(model) }}</span>
            <i title="Current selected model, click on Explore models to change your selection" class="fa fa-info-circle"></i>
          </span>
          <div class="navbar-burger" :class="{ 'is-active': isMobileMenu }"
            @click="isMobileMenu = !isMobileMenu">
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </div>
        </div>
        <div class="navbar-menu" id="#nav-menu" :class="{ 'is-active': isMobileMenu }">
          <div class="navbar-start">
          </div>
          <div class="navbar-end">
            <template v-for="menuItem, index in menuItems">
              <template v-if="Array.isArray(menuItem)">
                <div class="navbar-item has-dropdown is-hoverable is-unselectable">
                  <a class="navbar-link"
                  :class="{ 'is-active': menuItem[0] === activeDropMenu }"
                  @click="goToPage(menuItem[0])">
                    {{ menuItem[0] }}
                  </a>
                  <div class="navbar-dropdown">
                    <a class="navbar-item is-primary is-unselectable"
                    v-for="submenu, index in menuItem" v-if="index !== 0"
                    @click="goToPage(submenu)">
                      {{ submenu }}
                    </a>
                  </div>
                </div>
              </template>
              <template v-else-if="menuItem === 'explore'">
                  <a class="navbar-item is-unselectable"
                   :class="{ 'is-active': isActiveRoute('ExplorerRoot') }"
                   @click="goToPage(menuItem)">
                   <span class="is-hidden-touch has-text-centered"><b>Explore<br>models</b></span>
                   <span class="is-hidden-desktop"><b>Explore models</b></span>
                 </a>
              </template>
              <template v-else>
                <a class="navbar-item is-unselectable"
                   :class="{ 'is-active': isActiveRoute(menuItem) }"
                   @click="goToPage(menuItem)"
                   v-html="menuItem"></a>
              </template>
            </template>
          </div>
        </div>
      </div>
    </nav>
    <keep-alive>
      <router-view></router-view>
    </keep-alive>
    <footer id="footer" class="footer has-background-light">
      <div class="columns">
        <div class="column is-2">
          <a @click="viewRelaseNotes">v1.0</a>
        </div>
        <div class="column is-8">
          <div class="content has-text-centered">
            <p v-html="$t('footerText')"></p>
            <p>
              <a href="http://www.chalmers.se"><img src="./assets/chalmers.png" /></a>
              <a href="https://kaw.wallenberg.org/"><img src="./assets/wallenberg.gif" /></a>
              <a href="https://www.kth.se/en/bio/centres/wcpr"><img src="./assets/wpcr.jpg" /></a>
              <a href="https://nbis.se/"><img src="./assets/nbislogo-green.png" /></a>
              <a href="https://www.scilifelab.se"><img src="./assets/scilifelab-green.png" /></a>
              <a href="https://www.sysbio.se"><img src="./assets/sysbio-logo.png" /></a>
            </p>
          </div>
        </div>
      </div>
    </footer>
    <div v-if="showCookieMsg" id="cookies" class="columns has-background-grey">
      <div class="column has-text-centered">
        <div class="has-text-white">
          We use cookies to enhance the usability of our website. <a class="has-text-white has-text-weight-semibold" href='/documentation#privacy' target='_blank'>More information</a>
          <a class="button is-small is-rounded is-success has-text-weight-bold" @click="showCookieMsg=false; acceptCookiePolicy()">
            <span class="icon is-small"><i class="fa fa-check"></i></span>
            <span>OKAY</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SvgIcon from './components/SvgIcon';
import Logo from './assets/logo.svg';
import router from './router';
import { default as EventBus } from './event-bus';
import { isCookiePolicyAccepted, acceptCookiePolicy } from './helpers/store';

export default {
  name: 'app',
  components: {
    SvgIcon,
  },
  data() {
    return {
      Logo,
      menuItems: [
        'explore',
        [this.$t('navBut1Title'),
          this.$t('navBut11Title'),
          this.$t('navBut12Title'),
        ],
        [this.$t('navBut2Title'),
          this.$t('navBut21Title'),
          this.$t('navBut22Title'),
          this.$t('navBut23Title'),
        ],
        this.$t('navBut3Title'),
        this.$t('navBut4Title'),
      ],
      showExploreInfo: false,
      activeBrowserBut: false,
      activeViewerBut: false,
      showCookieMsg: !isCookiePolicyAccepted(),
      acceptCookiePolicy,
      activeDropMenu: '',
      model: '',
      browserLastPath: '',
      isMobileMenu: false,
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.saveBrowserPath();
      this.setupButons();
    },
  },
  beforeMount() {
    EventBus.$on('modelSelected', (model) => {
      this.model = model;
    });
    EventBus.$on('showExploreInfo', () => {
      this.showExploreInfo = true;
    });
    EventBus.$on('hideExploreInfo', () => {
      this.showExploreInfo = false;
    });
  },
  created() {
    this.setupButons();
  },
  methods: {
    setupButons() {
      if (this.$route.name === 'browser' || this.$route.name === 'browserRoot') {
        this.showExploreInfo = true;
        this.activeBrowserBut = true;
        this.activeViewerBut = false;
        this.model = this.$route.params.model;
        // this.goToGemsBrowser();
        this.saveBrowserPath();
      } else if (this.$route.name === 'viewer' ||
        this.$route.name === 'viewerCompartment' ||
        this.$route.name === 'viewerSubsystem') {
        this.showExploreInfo = true;
        this.activeBrowserBut = false;
        this.activeViewerBut = true;
        this.model = this.$route.params.model;
        // this.goToGemsViewer();
      } else {
        this.showExploreInfo = false;
        this.activeBrowserBut = false;
        this.activeViewerBut = false;
      }
    },
    goToPage(name) {
      if (['tools', 'external databases', 'api'].includes(name.toLowerCase())) {
        if (name.toLowerCase() === 'external databases') {
          name = 'databases'; // eslint-disable-line no-param-reassign
        }
        router.push(`/resources#${name.toLowerCase()}`);
      } else if (['compare', 'download'].includes(name.toLowerCase())) {
        router.push(`/gems/${name.toLowerCase()}`);
      } else {
        router.push(`/${name.toLowerCase()}`);
      }
    },
    isActiveRoute(name) {
      if (this.$route.name) {
        if (Array.isArray(name)) {
          return name[0].toLowerCase() === this.$route.name.toLowerCase();
        }
        return name.toLowerCase() === this.$route.name.toLowerCase();
      }
      return false;
    },
    goToGemsBrowser() {
      if (this.browserLastPath) {
        this.$router.push(this.browserLastPath);
      } else {
        this.$router.push(`/explore/gem-browser/${this.model}`);
      }
    },
    goToGemsViewer() {
      this.$router.push(`/explore/map-viewer/${this.model}`);
    },
    saveBrowserPath() {
      if (this.$route.name === 'browser') {
        this.browserLastPath = this.$route.path;
      } else if (this.$route.name === 'browserRoot') {
        this.browserLastPath = '';
      }
    },
    viewRelaseNotes() {
      router.push({
        path: '/About#releaseNotes',
        query: {},
      });
    },
  },
};
</script>

<style lang='scss'>

$primary: #4E755A;
$primary-light: #beccc3;
$link: #006992;
$warning: #FFC67D;
$danger: #FF4D4D;
$info: #006992;

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

#app {
  display: flex;
  min-height: 100vh;
  flex-direction: column
}

#modelHeader {
  padding: 0.75rem;
  span {
    margin-right: 0.15rem;
  }
  i {
    color: gray;
  }
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

.navbar-menu {
  a {
    font-size: 1.15em;
  }
}

.navbar-brand {
  a {
    font-size: 1.15em;
    font-weight: 400;
    line-height: 1.5;
  }
}

.footer {
  padding-bottom: 1em;
  padding-top: 1em;
  img {
    max-height: 35px;
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
      color: white;
      padding-left: 1.5em;
    }
    a:hover {
      color: black;
      background-color: $primary-light;
      border-radius: 0;
    }
    .is-active {
      color: black;
      background-color: white;
      border-radius: 0;
    }
  }
  .margin-fix {
    margin-top: 1rem;
    margin-bottom: 1rem;
    margin-left: 0;
  }
  .homepage-submenu {
    margin-left: 1.25em;
  }
  .more-padding {
    padding: 3rem 3.75rem 3rem 3.75rem;
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
}

#cookies {
  margin-top: 5px;
  position: sticky;
  bottom: 0;
}

.navbar-burger span {
  height: 2px;
}

</style>
