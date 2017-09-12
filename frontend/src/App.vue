<template>
  <div id="app">
    <nav id="main-nav" class="nav">
      <div class="container">
        <div>
          <a id="logo" class="nav-item">
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
    <section class="section">
      <div class="container">
        <router-view></router-view>
      </div>
    </section>
    <footer class="footer">
      <div class="container">
        <div class="content has-text-centered">
          <p v-html="$t('footerText')"><p>
          <p>
            <a><img src="./assets/chalmers.png" /></a>
            <a><img src="./assets/wallenberg.gif" /></a>
            <a><img src="https://www.kth.se/polopoly_fs/1.654259!/image/Front.gif" /></a>
          </p>
        </div>
      </div>
    </footer>
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
      } else {
        router.push(name);
      }

      location.reload();
    },
    isActive(name) {
      return name.toLowerCase() === this.$route.name.toLowerCase();
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
  img {
    max-height: 75px;
  }
  sup {
    vertical-align: top;
  }
}

</style>
