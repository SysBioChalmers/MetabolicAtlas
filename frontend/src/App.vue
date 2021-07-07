<template>
  <div id="app" :class="{'fade-page': showGemSearch}">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
    <nav id="navbar" class="navbar has-background-primary-lighter" role="navigation" aria-label="main navigation">
      <transition name="fade">
        <gem-search v-show="showGemSearch" :handle-clear="() => showGemSearch = false" />
      </transition>
      <transition name="fade">
        <div v-show="!showGemSearch" class="container is-fullhd">
          <div class="navbar-brand ml-2">
            <router-link class="navbar-item" :to="{ name: 'home' }" active-class=""
                         @click.native="isMobileMenu = false">
              <img src="/img/logo.png" />
            </router-link>
            <div class="navbar-burger pr-2" :class="{ 'is-active': isMobileMenu }"
                 @click="isMobileMenu = !isMobileMenu">
              <span aria-hidden="true"></span>
              <span aria-hidden="true"></span>
              <span aria-hidden="true"></span>
            </div>
          </div>
          <div id="#nav-menu" class="navbar-menu mr-2" :class="{ 'is-active': isMobileMenu }">
            <div v-show="model" class="navbar-start has-text-centered" title="Click to change model or tool">
              <router-link v-if="$route.path.includes('/explore')"
                           id="selectedModelLink"
                           :to="{ name: 'explorer' }"
                           class="navbar-item is-size-4 has-text-primary has-text-weight-bold is-unselectable" exact>
                {{ model ? model.short_name : '' }}
              </router-link>
            </div>
            <div class="navbar-end has-background-primary-lighter">
              <a class="navbar-item" @click.stop.prevent="showGemSearch = true">
                <span class="icon is-large px-2 py-3">
                  <i id="search-icon" class="fa fa-search" />
                </span>
              </a>
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
                      <div class="navbar-dropdown has-background-primary-lighter p-0">
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
      </transition>
    </nav>
    <router-view></router-view>
    <ErrorPanel :message="errorMessage" @hideErrorPanel="errorMessage=''" />
    <footer id="footer" class="footer has-background-primary-lighter is-size-6 py-4">
      <div class="columns is-gapless mb-0">
        <div v-show="!showCompactFooter()" class="column is-full">
          <div class="content has-text-centered">
            <p>
              <a href="https://www.sysbio.se" title="SysBio">
                <img class="my-0 mx-2" src="/img/sysbio-logo.png" />
              </a>
              <a href="http://www.chalmers.se" title="Chalmers University of Technology">
                <img class="my-0 mx-2" src="/img/chalmers.png" />
              </a>
              <a href="https://kaw.wallenberg.org/" title="Knut and Alice Wallenberg Foundation">
                <img class="my-0 mx-2" src="/img/wallenberg.gif" />
              </a>
              <a href="https://www.kth.se/wcpr" title="CBH | KTH Royal Institute of Technology">
                <img class="my-0 mx-2" src="/img/wpcr.jpg" />
              </a>
              <a href="https://nbis.se/">
                <img class="my-0 mx-2" src="/img/nbislogo-green.png"
                     title="National Bioinformatics Infrastructure Sweden" />
              </a>
              <a href="https://www.scilifelab.se" title="Science for Life Laboratory (SciLifeLab)">
                <img class="my-0 mx-2" src="/img/scilifelab.png" />
              </a>
            </p>
          </div>
        </div>
      </div>
      <div class="columns is-gapless">
        <div v-show="!showCompactFooter()" class="column has-text-centered mt-1">
          <p>2021 ©
            <span class="is-hidden-touch">
              &nbsp;Department of Biology and Biological Engineering |
            </span>
            &nbsp;Chalmers University of Technology</p>
        </div>
        <div v-show="showCompactFooter()" class="column has-text-centered-mobile">
          <p>2021 © &nbsp;Chalmers University of Technology</p>
        </div>
      </div>
    </footer>
    <div v-if="showCookieMsg" id="cookies" class="has-background-grey">
      <div class="column has-text-centered p-1">
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

import axios from 'axios';
import { mapState } from 'vuex';
import ErrorPanel from '@/components/shared/ErrorPanel';
import GemSearch from '@/components/explorer/gemBrowser/GemSearch';
import { default as messages } from '@/helpers/messages';
import { isCookiePolicyAccepted, acceptCookiePolicy } from './helpers/store';

export default {
  name: 'App',
  components: {
    ErrorPanel,
    GemSearch,
  },
  data() {
    return {
      /* eslint-disable quote-props */
      menuElems: [
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
      showGemSearch: false,
      messages,
      errorMessage: '',
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
  },
  watch: {
    showGemSearch(show) {
      if (show) {
        setTimeout(() => {
          document.querySelector('#search').focus();
        });
      }
    },
  },
  created() {
    this.setupErrorCatcher();
  },
  methods: {
    setupErrorCatcher() {
      axios.interceptors.response.use(
        response => response,
        (error) => {
          if (error.response && error.response.status === 404) {
            this.errorMessage = messages.notFoundError;
          } else {
            this.errorMessage = messages.unknownError;
          }
          return Promise.reject(error);
        }
      );

      this.$router.afterEach(() => {
        if (this.errorMessage !== '') {
          this.errorMessage = '';
        }
      });
    },
    showCompactFooter() {
      return this.$route.name === 'viewer';
    },
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

.content h1,h2,h3,h4,h5,h6 {
  margin-top: 1em;
}

.card-fullheight {
  height: 100%;
}

.hoverable:hover {
  box-shadow: $shadow-primary-light;
}

#app {
  display: flex;
  min-height: 100vh;
  flex-direction: column;

  &.fade-page {
    height: 100vh;
    overflow: hidden;

    &::after {
      position: absolute;
      width: 100vw;
      height: 100vh;
      content: "";
      background: rgba(0, 0, 0, 0.75);
      z-index: 10;
    }
  }
}

.has-addons {
  .button {
    width: 8rem;
  }
}

#navbar {
  min-height: 52px;

  @media screen and (min-width: $tablet) {
    min-height: 56px;
  }

  @media screen and (min-width: $desktop) {
    min-height: 64px;
  }

  .fade-enter-active, .fade-leave-active {
    transition: opacity .3s ease-in-out;
  }

  .fade-enter, .fade-leave-to {
    opacity: 0;
  }

  .container {
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
    }
    .navbar-burger{
      height: 4rem;
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
}

.footer {
  img {
    max-height: 30px;
  }
}

#comparison-details, .table-template {
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

#integrated {
  .card {
    height: 100%;
    display: flex;
    flex-direction: column;
    .card-header {
      flex-grow: 1;
    }
  }
  margin-bottom: 2rem;
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
