<template>
  <div id="app" class="hero is-fullheight">
    <div class="hero-head">
      <nav id="main-nav" class="nav" style="box-shadow: none">
        <div class="container">
          <div>
            <a id="logo" class="nav-item" @click="goToPage('/')" >
              <svg-icon width="175" height="75" :glyph="Logo"></svg-icon>
            </a>
          </div>
          <div class="nav-right nav-menu">
            <a
               v-for="menuItem in menuItems"
               class="nav-item"
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
import Logo from './assets/logo.svg';
import router from './router';

export default {
  name: 'app',
  components: {
    SvgIcon,
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
    };
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
  },
};
</script>

<style lang='scss'>

$primary: #64CC9A;
$warning: #FFC67D;
$danger: #FF865C;

$body-size: 14px !default

$desktop: 1192px !default;
$widescreen: 1384px !default;
$fullhd: 1576px !default;

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

#main-nav {
  height: 75px;

  #logo {
    padding-left: 0;
  }
}

.nav-menu {
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

</style>
