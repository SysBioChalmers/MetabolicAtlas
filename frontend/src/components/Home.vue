<template>
  <div class="extended-section">
    <section class="hero video container" style="max-width:100%; width:100%;">
      <div class="hero-video is-transparent">
        <video poster="https://ftp.icsb.chalmers.se/.static/banner_video.jpg" playsinline autoplay muted loop>
          <source src="https://ftp.icsb.chalmers.se/.static/banner_video.mp4" type="video/mp4">
        </video>
      </div>
      <div class="hero-body">
        <div class="container has-text-centered">
          <h1 class="is-size-1 title has-text-primary">METABOLIC ATLAS</h1>
          <h2 class="is-size-2 has-text-gray">
            THE ATLAS FOR EXPLORATION OF METABOLISM
          </h2>
        </div>
      </div>
    </section>
    <section class="section">
      <div id="home" class="container">
        <div class="columns">
          <div class="column">
            <div class="card">
              <div id="mobileMenu" class="columns is-mobile is-multiline margin-fix">
                <div class="column is-narrow is-full-mobile has-background-primary has-text-weight-bold is-paddingless">
                  <aside class="menu">
                    <ul class="menu-list is-size-5 is-unselectable">
                      <li v-for="menuItem in menu">
                        <a @click="selectMenu(menuItem)" :class="[ {'is-active' : menuItem.title === currentMenu.title}]">{{ menuItem.title}}</a>
                      </li>
                    </ul>
                  </aside>
                </div>
                <div class="column is-full-mobile more-padding">
                  <p class="is-size-5 has-text-justified" v-html="currentMenu.text"></p>
                </div>
                <div class="column is-full-mobile more-padding is-v-aligned">
                  <router-link :to="currentMenu.url">
                    <div class="card" :class="{ 'card-selectable': currentMenu.cardLink}">
                      <img :src="currentMenu.img" :alt="currentMenu.title"/>
                      <template v-if="currentMenu.cardLink">
                        <footer class="card-footer has-text-centered has-background-primary-lighter">
                          <a class="card-footer-item is-size-5 has-text-weight-bold">{{ currentMenu.cardLink }}</a>
                        </footer>
                      </template>
                    </div>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div id="newsandcommunity" class="columns is-variable is-6">
          <div class="column is-half" v-for="card in cards">
            <div class="card card-fullheight is-size-5">
              <header class="card-header has-background-primary">
                <p class="card-content has-text-weight-bold has-text-white">{{ card.title }}</p>
              </header>
              <div class="card-content has-text-justified">
                <p v-for="el in card.text">
                  <span v-if="el[0]"><b>{{ el[0] }}</b> - </span><span v-html="el[1]"></span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { default as messages } from '../helpers/messages';

/* eslint-disable global-require*/
export default {
  name: 'home',
  data() {
    return {
      menu: [
        { title: 'Welcome',
          text: 'The <b>Metabolic Atlas</b> integrates open source genome-scale metabolic models (GEMs) of human and yeast for easy browsing and analysis. It also contains many more genome scale metabolic models constructed by our organization.<br><br>Detailed biochemical information is provided for individual model components, such as reactions, metabolites, and genes. These components are also associated with standard identifiers, facilitating integration with external databases, such as the Human Protein Atlas. <br><br><i>Article under consideration</i>',
          img: require('../assets/explorer.jpg'),
          cardLink: 'Explore',
          url: { name: 'explorerRoot' } },
        { title: messages.gemBrowserName,
          text: 'The <b>GEM Browser</b> enables powerful query and exploration of model content in tabular format.<br><br>A wide range of attributes, including reaction equations, metabolite formulas, gene rules and subsystem contents, are presented as a detailed network of individual model components. They are highly interconnected and rationally associated to easily navigate and switch between them.<br><br>Visit the documentation to learn about the different functionalities provided by the GEM Browser.',
          img: require('../assets/gemBrowser.jpg'),
          cardLink: 'Explore Human1 on the GEM Browser',
          url: { name: 'browserRoot', params: { model: 'hmr2' } } },
        { title: messages.interPartName,
          text: `The <b>Interaction Partners</b> graph shows connectivity between metabolites and enzymes based on their associated reactions.<br><br>The graph is dynamically generated and is customizable. One can interact with a restricted part of the metabolic network, or further expand the interaction partners of any element already on the graph. Moreover, RNA expression data from the Human Protein Atlas can be overlaid onto the graph. <br><br>This feature is available only for metabolites and enzymes, and is accessible via the <b>${messages.gemBrowserName}</b>.`,
          img: require('../assets/interaction.jpg'),
          url: { name: 'explorerRoot' } },
        { title: messages.mapViewerName,
          text: 'For each of the integrated models, the <b>Metabolic Atlas</b> automatically generates 3D graph at both compartment and subsystem level.<br><br>Both compartment and subsystem maps of the human-GEM are manually curated. On these maps, one can search for reactions, metabolites or genes. Moreover, RNA expression data from Human Protein Atlas can be overlaid.<br><br>By clicking on an element on the map, more information of that element will be shown on the left sidebar. From there, one can navigate back to the <b>GEM Browser</b> for detailed information.',
          img: require('../assets/mapViewer.jpg'),
          cardLink: 'Explore Human1 on the Map Viewer',
          url: { name: 'viewer', params: { model: 'hmr2' } } },
        { title: 'Search',
          text: 'The menu bar contains a shortcut to the <b>Global search</b> function, which enables users to easily search cellular components across all the integrated models. Further filtering is also available, based on result type (e.g. metabolite) and its parameters (e.g. compartment).<br><br>For retrieving larger subsets of the model, model we recommend experienced users to use our the API. Alternatively, models can be downloaded from the <b>GEM repository</b> page or from their original repository on GitHub.<br><br>',
          img: require('../assets/search.jpg'),
          cardLink: 'Global search',
          url: { name: 'search' } },
        { title: 'Export',
          text: '<b>Metabolic Atlas</b> provides open access to the models and associated annotations. Most of the data provided on <b>Metabolic Atlas</b> is convenient to export, look for export buttons.<br><br>For the ones interested in extracting data in JSON format, we have documented our API. When using images or files obtained from our website, use the following reference:<br><br><i>Article under consideration</i>',
          img: require('../assets/export.jpg'),
          url: '' },
        { title: 'Analyze',
          text: 'Currently, only RNA expression data from the Human Protein Atlas can be viewed in the 2D Map Viewer and Interaction Partners.<br><br>This feature is still under development.',
          img: require('../assets/analyze.jpg'),
          url: '' },
        { title: 'GEM repository',
          text: 'Over 350 GEMs can be downloaded from the browser or directly from the <b>Metabolic Atlas FTP server</b>. The tabular view enables customized selection.<br><br>Clicking on each of the models brings up more information about the model, including a text description and, if available, references.',
          img: require('../assets/gems.jpg'),
          cardLink: 'GEM repository',
          url: { name: 'gems' } },
        { title: 'Resources',
          text: 'Working with metabolic models requires a set of tools and external databases, which we have collected for one-click access.<br><br>Additionally, the Metabolic Atlas database is open to further integrations.',
          img: require('../assets/resources.jpg'),
          url: { name: 'resources' } },
      ],
      currentMenu: {},
      cards: [
        { title: 'Latest news',
          text: [
            ['2018.12.17', 'MapViewer is speedier at browsing manually curated maps'],
            ['2018.12.08', 'New maps for <i>Human1</i> are being created'],
            ['2018.11.28', 'The <i>Human1</i> model is now integrated'],
            ['2018.11.23', 'The <i>Yeast8</i> model is now integrated'],
          ],
        },
        { title: 'Community',
          text: [['', '<p>We are grateful for the efforts of scientists all over the world into in creating the knowledge required to assemble high quality genome scale metabolic models and are passionate about continuing on this journey of open curation of models.<br><br>We invite you to explore the world of GEMs through Metabolic Atlas, and hope it will enhance your interest in this field. We wish to continuously improve the Metabolic Atlas for the community. Contact us with any feedback, suggestions, or requests.</p>']],
        },
      ],
    };
  },
  beforeMount() {
    this.currentMenu = this.menu[0];
  },
  methods: {
    selectMenu(newMenu) {
      this.currentMenu = newMenu;
    },
  },
};

</script>
<style lang="scss">
</style>
