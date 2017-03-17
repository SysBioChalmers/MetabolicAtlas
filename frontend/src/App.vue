<template>
  <div id="app">
    <nav id="main-nav" class="nav">
      <div class="container">
        <div class="container">
          <a id="logo" class="nav-item">
            <svg-logo></svg-logo>
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

import SvgLogo from './components/SvgLogo';

export default {
  name: 'app',
  components: {
    SvgLogo,
  },
};
</script>

<style lang='scss'>

$primary: #64CC9A;

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

sup {
  vertical-align: bottom;
  font-size: 0.7em;
}


#main-nav {
  height: 75px;

  #logo {
    padding-left: 0;
    max-height: 75px;
    max-width: 175px;

    .metabolite:hover {
      @include animation('rotating 1.7s linear infinite;');
    }
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
