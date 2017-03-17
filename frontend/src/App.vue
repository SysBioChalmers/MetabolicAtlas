<template>
  <div id="app">
    <nav id="main-nav" class="nav">
      <div class="container">
        <div class="container">
          <a id="logo" class="nav-item">
            <svg-icon width="175" height="75" :glyph="Logo"></svg-icon>
          </a>
        </div>
        <div class="nav-right nav-menu">
          <a class="nav-item is-active">network graph</a>
          <a class="nav-item">models</a>
          <a class="nav-item">resources</a>
          <a class="nav-item">about</a>
          <a class="nav-item">contact</a>
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
          <p>
            Chalmers University of Technology | Department of Biology and Biological Engineering |
            <a href="http://sysbio.se" target="blank">Sys<sup>2</sup>Bio</a>
          <p>
          <p>
            <a><img src="./assets/chalmers.png" /></a>
            <a><img src="./assets/wallenberg.gif" /></a>
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>

import SvgIcon from './components/SvgIcon';
import Logo from './assets/logo.svg';

export default {
  name: 'app',
  components: {
    SvgIcon,
  },
  data() {
    return { Logo };
  },
};
</script>

<style lang='scss'>

$primary: #64CC9A;

@import '~bulma';

sup {
  vertical-align: bottom;
  font-size: 0.7em;
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
