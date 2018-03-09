<template>
  <div id="app" class="hero is-fullheight">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
    <transition name="fade">
      <metabolic-viewer id="metabolicViewer" v-show="isMetabolicViewer"
      :model="{ id: selectedModel, name: modelsName[selectedModel] }"></metabolic-viewer>
    </transition>
    <div class="hero-head">
      <nav class="navbar is-light" role="navigation" aria-label="main navigation">
        <div class="container">
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
              <template v-for="menuItem, index in menuItems">
                <template v-if="index === 0">
                  <div class="navbar-item has-dropdown is-hoverable">
                    <a class="navbar-link"  @click="goToPage('', selectedModel)">
                      {{ menuItem }}
                      &nbsp;<span class="tag is-info is-large">{{ modelsName[selectedModel] }}</span>
                    </a>
                    <div class="navbar-dropdown">
                      <a class="navbar-item is-primary"
                        v-for="model in models"
                        @click="goToPage('', model)">
                        {{ modelsName[model] }}
                      </a>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <template v-if="Array.isArray(menuItem)">
                    <div class="navbar-item has-dropdown is-hoverable">
                      <a class="navbar-link" @click="goToPage(menuItem[0])">
                        {{ menuItem[0] }}
                      </a>
                      <div class="navbar-dropdown">
                        <a class="navbar-item is-primary" 
                        v-for="submenu, index in menuItem" v-if="index != 0"
                        @click="goToPage(menuItem[index])">
                          {{ menuItem[index] }}
                        </a>
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <a
                       class="navbar-item"
                       :class="[{ 'is-active': isActive(menuItem) }, '']"
                       @click="goToPage(menuItem)"
                    >{{ menuItem }}</a>
                  </template>
                </template>
              </template>
            </div>
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
        <div class="columns">
          <div class="column is-2">
          </div>
          <div class="column is-8">
            <div class="content has-text-centered">
              <p v-html="$t('footerText')"><p>
              <p>
                <a href="http://www.chalmers.se"><img src="./assets/chalmers.png" /></a>
                <a href="https://kaw.wallenberg.org/"><img src="./assets/wallenberg.gif" /></a>
                <a href="https://www.kth.se/en/bio/centres/wcpr"><img src="./assets/wpcr.jpg" /></a>
              </p>
            </div>
          </div>
          <div class="column is-2">
            <div class="is-pulled-right">
              <a @click="viewRelaseNotes">Release v1.0</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>

import SvgIcon from './components/SvgIcon';
import MetabolicViewer from './components/MetabolicViewer';
import Logo from './assets/logo.svg';
import router from './router';
import { default as EventBus } from './event-bus';


export default {
  name: 'app',
  components: {
    SvgIcon,
    MetabolicViewer,
  },
  data() {
    return {
      Logo,
      modelsName: {
        hmr2: this.$t('hmr2'),
      },
      models: [
        'hmr2',
      ],
      menuItems: [
        this.$t('navBut1Title'),
        this.$t('navBut2Title'),
        [this.$t('navBut3Title'),
          this.$t('navBut31Title'),
          this.$t('navBut32Title'),
          this.$t('navBut33Title'),
        ],
        this.$t('navBut4Title'),
        this.$t('navBut5Title'),
        this.$t('navBut6Title'),
      ],
      isMetabolicViewer: false,
      selectedModel: 'hmr2',
    };
  },
  created() {
    EventBus.$on('requestViewer', (type, name, secondaryName, ids) => {
      this.isMetabolicViewer = true;
      console.log(`requestViewer ${type}, ${name}, ${secondaryName}, ${ids}`);
      EventBus.$emit('showAction', type, name, secondaryName, ids);
    });
    EventBus.$on('toggleNetworkGraph', () => {
      this.isMetabolicViewer = !this.isMetabolicViewer;
    });
  },
  methods: {
    goToPage(name, model) {
      // TODO: make this not hard-coded
      if (model) {
        router.push(
          {
            path: `/GemsExplorer/${model}`,
          },
        );
      } else if (['tools', 'external databases', 'api'].includes(name.toLowerCase())) {
        if (name.toLowerCase() === 'external databases') {
          name = 'databases'; // eslint-disable-line no-param-reassign
        }
        router.push(`/Resources#${name.toLowerCase()}`);
      } else {
        router.push(`/${name}`);
      }
    },
    isActive(name) {
      if (this.$route.name) {
        if (Array.isArray(name)) {
          return name[0].toLowerCase() === this.$route.name.toLowerCase();
        }
        return name.toLowerCase() === this.$route.name.toLowerCase();
      }
      return false;
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

#metabolicViewer {
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

/* FIXME .is-light overwritten somewhere */
.navbar.is-light {
  background: whitesmoke;
}

.navbar-menu {
  a {
    font-size: 1.15em;
  }
}

.footer {
  padding-bottom: 1em;
  padding-top: 1em;
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


