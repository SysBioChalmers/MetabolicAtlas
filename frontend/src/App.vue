<template>
  <div id="app">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
    <nav id="navbar" class="navbar is-light" role="navigation" aria-label="main navigation">
      <div class="container">
        <div class="navbar-brand">
          <a id="logo" class="navbar-item" @click="goToPage('')" >
            <svg-icon width="175" height="75" :glyph="Logo"></svg-icon>
          </a>
          <div class="navbar-burger">
            <span
               v-show="false"
               v-for="menuItem in menuItems"
               :class="{ 'is-active': isActiveRoute(menuItem) }"
               @click="goToPage(menuItem)"
            >{{ menuItem }}</span>
          </div>
        </div>
        <div class="navbar-menu" id="#nav-menu">
          <div class="navbar-start">
            <div class="navbar-item">
              <div class="buttons has-addons">
                <span class="button is-medium"
                :class="[{ 'is-selected': showGemsExplorer }, { 'is-info': showGemsExplorer }]"
                @click="goToPage('gemsExplorer', selectedModel)"
                >Explorer</span>
                <span class="button is-medium"
                :class="[{ 'is-selected': showMetabolicViewer }, { 'is-info': showMetabolicViewer }]"
                @click="goToPage('metabolicViewer', selectedModel)"
                >Maps</span>
              </div>
            </div>
            <div class="navbar-item has-dropdown is-hoverable">
              <a class="navbar-link"  @click="goToPage('gemsExplorer', selectedModel)">
                Model:
                &nbsp;<span class="tag is-info is-medium">{{ models[selectedModel].short_name }}</span>
              </a>
              <div class="navbar-dropdown">
                <a class="navbar-item is-primary"
                  v-for="model, k in models"
                  @click="goToPage('gemsExplorer', model.database_name)" v-html="getModelDescription(model)">
                </a>
              </div>
            </div>
          </div>
          <div class="navbar-end">
            <template v-for="menuItem, index in menuItems">
              <template v-if="Array.isArray(menuItem)">
                <div class="navbar-item has-dropdown is-hoverable">
                  <a class="navbar-link" 
                  :class="{ 'is-active': menuItem[0] === activeDropMenu }"
                  @click="goToPage(menuItem[0], '', menuItem[0])">
                    {{ menuItem[0] }}
                  </a>
                  <div class="navbar-dropdown">
                    <a class="navbar-item is-primary" 
                    v-for="submenu, index in menuItem" v-if="index != 0"
                    @click="goToPage(submenu, '', menuItem[0])">
                      {{ submenu }}
                    </a>
                  </div>
                </div>
              </template>
              <template v-else>
                <a
                   class="navbar-item"
                   :class="{ 'is-active': isActiveRoute(menuItem) }"
                   @click="goToPage(menuItem, '', '')"
                >{{ menuItem }}</a>
              </template>
            </template>
          </div>
        </div>
      </div>
    </nav>
    <keep-alive>
      <router-view :selectedModel="selectedModel"></router-view>
    </keep-alive>
    <footer id="footer" class="footer">
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
</template>

<script>
import $ from 'jquery';
import axios from 'axios';
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
      models: { hmr2: { short_name: '' }, hmr2n: { short_name: '' } },
      menuItems: [
        this.$t('navBut1Title'),
        [this.$t('navBut2Title'),
          this.$t('navBut21Title'),
          this.$t('navBut22Title'),
          this.$t('navBut23Title'),
        ],
        this.$t('navBut3Title'),
        this.$t('navBut4Title'),
      ],
      showMetabolicViewer: true,
      showGemsExplorer: false,
      selectedModel: 'hmr2',
      activeDropMenu: '',
    };
  },
  beforeMount() {
    // get models list
    axios.get('models/')
      .then((response) => {
        const models = {};
        for (const model of response.data) {
          models[model.database_name] = model;
        }
        this.models = models;
      })
      .catch(() => {
        this.errorMessage = this.$t('unknownError');
      });

    $('body').on('click', 'td m', function f() {
      if (!($(this).hasClass('cms'))) {
        EventBus.$emit('updateSelTab', 'metabolite', $(this).attr('class'));
      }
    });
  },
  created() {
    EventBus.$on('requestViewer', (type, name, secondaryName, ids) => {
      this.showMetabolicViewer = true;
      console.log(`requestViewer ${type}, ${name}, ${secondaryName}, ${ids}`);
      EventBus.$emit('showAction', type, name, secondaryName, ids);
    });
    EventBus.$on('showMetabolicViewer', () => {
      this.showMetabolicViewer = true;
      this.showGemsExplorer = false;
      this.goToPage('metabolicViewer', this.selectedModel, '');
    });
    EventBus.$on('showGemsExplorer', () => {
      this.showMetabolicViewer = false;
      this.showGemsExplorer = true;
    });
    // document.body.addEventListener('keyup', (e) => {
    //   if (e.keyCode === 27) {
    //     this.showMetabolicViewer = false;
    //   }
    // });
  },
  methods: {
    getModelDescription(model) {
      return `<div>${model.short_name} - ${model.name}<div>
      <div class="has-text-grey">
        ${model.reaction_count} reactions -
        ${model.metabolite_count} metabolites -
        <br>${model.enzyme_count} enzymes
      </div>`;
    },
    goToPage(name, model, activeMenu) {
      // TODO: make this not hard-coded
      this.activeDropMenu = activeMenu;
      if (name.toLowerCase() === 'gemsexplorer') {
        this.showGemsExplorer = true;
        this.showMetabolicViewer = false;
      } else if (name.toLowerCase() === 'metabolicviewer') {
        this.showGemsExplorer = false;
        this.showMetabolicViewer = true;
      }
      if (model) {
        router.push({ path: `/${name}/${model}` });
      } else if (['tools', 'external databases', 'api'].includes(name.toLowerCase())) {
        if (name.toLowerCase() === 'external databases') {
          name = 'databases'; // eslint-disable-line no-param-reassign
        }
        router.push(`/Resources#${name.toLowerCase()}`);
      } else {
        router.push(`/${name}`);
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
$link: #006992;
$warning: #FFC67D;
$danger: #FF865C;
$info: #006992;

$body-size: 14px !default

$desktop: 1192px !default;
$widescreen: 1384px !default;
$fullhd: 1576px !default;
$switch-background: $primary;


/* @import "./sass/extensions/_all" FIX ME */
@import '~bulma';
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

.extended-section {
  flex: 1;
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

#HPARNAexpLegend {
  margin: auto;
  border-radius: 0;
  .title {
    margin-bottom: 0.3em;
  }

  .exp-lvl-legend {
    list-style: none;
    li {
      display: inline-block;
      margin-left: 7px;
      line-height: 15px;
      &:first-child {
        margin-left: 0;
      }
    }
  }

  span {
    float: left;
    margin: 0 2px 2px 2px;
    width: 15px;
    height: 15px;
    display: block;
    border: 1px solid black;
  }
}

</style>


