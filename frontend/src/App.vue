<template>
  <div id="app">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
    <nav id="navbar" class="navbar has-background-primary-lighter" role="navigation" aria-label="main navigation">
      <div class="container is-fullhd">
        <div class="navbar-brand">
          <router-link class="navbar-item" :to="{ name: 'home' }" active-class="" @click.native="isMobileMenu = false">
            <img :src="require('./assets/logo.png')" />
          </router-link>
          <div class="navbar-burger" :class="{ 'is-active': isMobileMenu }" @click="isMobileMenu = !isMobileMenu">
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </div>
        </div>
        <div id="#nav-menu" class="navbar-menu" :class="{ 'is-active': isMobileMenu }">
          <div v-show="model" class="navbar-start has-text-centered" title="Click to change model or tool">
            <router-link id="selectedModelLink"
                         v-if="$route.path.includes('/explore')"
                         :to="{ name: 'explorer' }"
                         class="navbar-item is-size-4 has-text-primary has-text-weight-bold is-unselectable" exact>
              {{ model ? model.short_name : '' }}
            </router-link>
          </div>
          <div class="navbar-end has-background-primary-lighter">
            <template v-for="(menuElem) in menuElems">
              <template v-if="menuElem.routeName">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <router-link class="navbar-item is-unselectable is-active-underline"
                             :to="{ name: menuElem.routeName }"
                             @click.native="isMobileMenu = false" v-html="menuElem.displayName">
                </router-link>
              </template>
              <template v-else>
                <template>
                  <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                  <div class="navbar-item has-dropdown is-hoverable is-unselectable has-background-primary-lighter">
                    <a class="navbar-link is-active-underline"
                       :class="{
                         'router-link-active': menuElem.subMenuElems.map(sme => sme.routeName).includes($route.name)
                       }">
                      {{ menuElem.displayName }}
                    </a>
                    <div class="navbar-dropdown has-background-primary-lighter is-paddingless">
                      <template v-for="(subMenuElem) in menuElem.subMenuElems">
                        <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                        <router-link class="navbar-item is-unselectable has-background-primary-lighter"
                                     :to="{ name: subMenuElem.routeName }"
                                     @click.native="isMobileMenu = false">{{ subMenuElem.displayName }}
                        </router-link>
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
          <p>2020 © Department of Biology and Biological Engineering | Chalmers University of Technology</p>
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
                <img src="./assets/nbislogo-green.png" title="National Bioinformatics Infrastructure Sweden" />
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
      <div class="column has-text-centered" style="padding: 0.25rem">
        <div class="has-text-white">
          We use cookies to enhance the usability of our website.
          By continuing you are agreeing to our
          <router-link class="has-text-white has-text-weight-bold"
                       :to="{ name: 'about', hash: '#privacy' }">
            Privacy Notice and Terms of Use
          </router-link>&emsp;
          <p class="button is-small is-rounded has-background-danger has-text-white has-text-weight-bold"
             @click="showCookieMsg=false; acceptCookiePolicy()">
            <span class="icon is-small"><i class="fa fa-check"></i></span>
            <span>OKAY</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import { mapState } from 'vuex';
import { isCookiePolicyAccepted, acceptCookiePolicy } from './helpers/store';

export default {
  name: 'App',
  data() {
    return {
      /* eslint-disable quote-props */
      menuElems: [
        {
          displayName: '<span class="icon is-large"><i id="search-icon" class="fa fa-search"></i></span>',
          routeName: 'search',
        },
        {
          displayName: 'Explore',
          routeName: 'explorer',
        },
        {
          displayName: 'GEM',
          subMenuElems: [
            {
              displayName: 'Repository',
              routeName: 'gems',
            },
            {
              displayName: 'Comparison',
              routeName: 'comparemodels',
            },
          ],
        },
        {
          displayName: 'Resources',
          routeName: 'resources',
        },
        {
          displayName: 'Documentation',
          routeName: 'documentation',
        },
        {
          displayName: 'About',
          routeName: 'about',
        },
      ],
      showCookieMsg: navigator.doNotTrack !== '1' && !isCookiePolicyAccepted(),
      acceptCookiePolicy,
      activeDropMenu: '',
      browserLastRoute: {},
      viewerLastRoute: {},
      isMobileMenu: false,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
  },
};
</script>

<style lang='scss'>

@import '~bulma';
@import '~bulma-timeline';


html {
  @include mobile {
    font-size: 13px;
  }
  @include tablet {
    font-size: 14px;
  }
  @include desktop {
    font-size: 16px; // Bulma default
  }
}

.extended-section {
  flex: 1;
}

.has-background-primary-lighter {
  background-color: $primary-lighter;
}

.has-background-lightgray {
  background-color: lightgray;
}

.card-margin {
  margin: 0.75rem;
}

m, .clickable {
  cursor: pointer;
}

.card-content-compact {
  padding: 0.75rem;
}


.content h1,h2,h3,h4,h5,h6 {
  margin-top: 1em;
}

.card-fullheight {
  height: 100%;
}

.hoverable:hover {
  box-shadow: $shadow-primary-light;
}

.section-no-top {
  padding-top: 0;
}

#app {
  display: flex;
  min-height: 100vh;
  flex-direction: column
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
  .router-link-active {
    color: $black-bis;
    background-color: $grey-lighter;
    &.is-active-underline {
      color: $black-bis;
      background-color: $grey-lighter;
      border-bottom: 1px solid $primary;
    }
  }
  .navbar-brand {
    a {
      font-weight: 400;
    }
    margin-left: 0.5rem;
  }
  .navbar-menu {
    margin-right: 0.5rem;
  }
  .navbar-burger{
    height: 4rem;
    padding-right: 0.5rem;
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

  #search-icon {
    font-size: 1.8rem;
  }
  #selectedModelLink .router-link-exact-active, .router-link-active {
    background-color: $primary-lighter;
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

.metabolite-table, .model-table, .reaction-table, .subsystem-table {
  .main-table tr td.td-key, #ed-table tr td.td-key {
    width: 150px;
  }
  font-size: 0.93em;
  .tag {
    font-size: 0.93em;
  }
}

#cookies {
  position: sticky;
  bottom: 0;
  .button:not(:hover) {
    border-color: transparent;
  }
}

#cytoTable .tag {
  height: 1.4rem;
  margin: 2px 3px;
  user-select: none;
  &.hl {
    background: $primary;
    color: whitesmoke;
  }
}

#integrated {
  .card {
    height: 100%;
    display: flex;
    flex-direction: column;
    .card-header {
      flex-grow: 1;
    }
    .card-footer {
    }
  }
  margin-bottom: 2rem;
}

#gem-list-modal {
  .modal-content {
    padding: 2rem;
  }
}

#documentation hr {
   margin-top: 2.75rem;
}

span.sc {
  border-radius: 10px;
  background: lightgray;
  padding-right: 4px;
  padding-left: 3px;
}

// CSS from nprogress https://github.com/rstacruz/nprogress/blob/master/nprogress.css
/* Make clicks pass-through */
#nprogress {
  pointer-events: none;
}

#nprogress .bar {
  background: $warning;
  position: fixed;
  z-index: 1000;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
}

</style>
