<template>
  <div class="extended-section">
    <section class="hero is-large is-primary is-bold">
      <div class="hero-body has-text-centered">
        <p class="is-size-1 title has-text-white">METABOLIC ATLAS 2.0</p>
      </div>
    </section>

    <!-- TODO fix mobile layout -->
    <section id="home">
      <div v-for="menuItem in menu" :key="menuItem.title"
           class="stripe as-background-white-ter">
       <div class="container is-fullhd py-6">
          <div class="columns is-variable is-8 is-vcentered py-6">
            <div class="column is-1"></div>
            <div class="column is-5 is-size-5">
              <p class="title is-size-4 has-text-centered has-text-primary">
                {{ menuItem.title }}
                <span class="icon is-large fa-lg">
                  <i :class="`fa fa-${menuItem.icon}`"></i>
                </span>
              </p>
              <p v-html="menuItem.text"></p>
            </div>
            <div class="column">
              <router-link :to="menuItem.route">
                <div class="card" :class="{ 'hoverable': menuItem.cardLink}">
                  <img :src="menuItem.img" :alt="menuItem.title" />
                  <template v-if="menuItem.cardLink">
                    <footer class="card-footer has-text-centered">
                      <a class="card-footer-item has-text-weight-bold is-size-5">
                        {{ menuItem.cardLink }}
                      </a>
                    </footer>
                  </template>
                </div>
              </router-link>
            </div>
            <div class="column is-1"></div>
          </div>
        </div>
      </div>

      <div class="container is-fullhd">
        <div class="columns is-variable is-6">
          <div v-for="card in cards" :key="card.title" class="column is-5">
            <div class="card card-fullheight">
              <header class="card-header has-background-success ">
                <p class="card-content py-2 has-text-weight-bold has-text-white">{{ card.title }}</p>
              </header>
              <div class="card-content has-text-justified">
                <table>
                  <template v-for="el in card.text">
                    <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                    <tr v-if="el.date">
                      <td>{{ el.date }}</td>
                      <td>
                        <router-link :to="{ name: 'about', hash: `#${el.hash}` }">
                          {{ el.text }}
                        </router-link>
                      </td>
                    </tr>
                    <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                    <tr v-else>
                      <span v-html="el.text"></span>
                    </tr>
                  </template>
                </table>
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

/* eslint-disable global-require */
export default {
  name: 'Home',
  data() {
    return {
      menu: [
        { title: 'Welcome',
          text: '<b>Metabolic Atlas</b> integrates open source genome-scale metabolic models (GEMs) of human and yeast for easy browsing and analysis. It also contains many more GEMs constructed by our organization.<br><br>Detailed biochemical information is provided for individual model components, such as reactions, metabolites, and genes. These components are also associated with standard identifiers, facilitating integration with external databases, such as the Human Protein Atlas. <br><br><a href="https://doi.org/10.1126/scisignal.aaz1482" target="_blank">Robinson, J., et al, 2020. <i>An atlas of human metabolism</i>. Sci. Signal. 13, eaaz1482 </a>',
          img: require('../assets/explorer.jpg'),
          cardLink: 'Explore a GEM',
          route: { name: 'explorer' },
          icon: 'home' },
        { title: 'Latest news',
          text: 'Lorem ipsum',
          img: require('../assets/explorer.jpg'),
          cardLink: 'Explore a GEM',
          route: { name: 'news' },
          icon: 'newspaper-o' },
        { title: messages.gemBrowserName,
          text: 'The <b>GEM Browser</b> enables powerful query and exploration of model content in tabular format.<br><br>A wide range of attributes, including reaction equations, metabolite formulas, gene rules and subsystem contents, are presented as a detailed network of individual model components. They are highly interconnected and rationally associated to easily navigate and switch between them.<br><br>Visit the documentation to learn about the different functionalities provided by the GEM Browser.',
          img: require('../assets/gemBrowser.jpg'),
          cardLink: 'Explore Human-GEM with the GEM Browser',
          route: { name: 'browser', params: { model: 'Human-GEM' } },
          icon: 'table' },
        { title: messages.mapViewerName,
          text: 'For easy visualization, <b>Metabolic Atlas</b> handles both 2D and 3D maps. For each of the integrated models, the website automatically generates 3D graphs at both compartment and subsystem level.<br><br>Both compartment and subsystem 2D maps of the Human-GEM have been created by the contributors to Human-GEM and are manually curated. On these maps, one can search for reactions, metabolites or genes. Moreover, RNA expression data from Human Protein Atlas can be overlaid.<br><br>By clicking on an element on the map, more information of that element will be shown on the left sidebar. From there, one can navigate back to the <b>GEM Browser</b> for detailed information.',
          img: require('../assets/mapViewer.jpg'),
          cardLink: 'Explore the Golgi apparatus with the Map Viewer',
          route: { name: 'viewer',
            params: { model: 'Human-GEM', type: 'compartment', map_id: 'golgi_apparatus' },
            query: { dim: '2d' } },
          icon: 'map-o' },
        { title: messages.interPartName,
          text: `The <b>Interaction Partners</b> graph shows connectivity between metabolites and genes based on their associated reactions.<br><br>The graph is dynamically generated and is customizable. One can interact with a restricted part of the metabolic network, or further expand the interaction partners of any element already on the graph. Moreover, RNA expression data from the Human Protein Atlas can be overlaid onto the graph. <br><br>This feature is available only for metabolites and genes, and is accessible via the <b>${messages.gemBrowserName}</b>.`,
          img: require('../assets/interaction.jpg'),
          cardLink: 'View glyoxalate[p] in Interaction Partners',
          route: { name: 'interaction', params: { model: 'Human-GEM', id: 'm02007p' } },
          icon: 'connectdevelop' },
        { title: 'Search',
          text: 'The menu bar contains a shortcut to the <b>Global search</b> function, which enables users to easily search cellular components across all the integrated models. Further filtering is also available, based on result type (e.g. metabolite) and its parameters (e.g. compartment).<br><br>For retrieving larger subsets of the model, we recommend experienced users to use our the API. Alternatively, models can be downloaded from the <b>GEM Repository</b> page or from their original repository on GitHub.<br><br>',
          img: require('../assets/search.jpg'),
          cardLink: 'Search within all integrated GEMs',
          route: { name: 'search', query: { term: '' } },
          icon: 'search' },
        { title: 'Analyze',
          text: 'Gene expression data from the Human Protein Atlas can be viewed in the 2D and 3D maps and Interaction Partners. User data can also be overlaid onto the maps, with the option of comparing datasets, for example against normal tissue.<br><br>Additional types of omics integrations are under development.',
          cardLink: 'Compare gene expression in the endoplasmic reticulum',
          img: require('../assets/analyze.jpg'),
          route: { name: 'viewer',
            params: { model: 'Human-GEM', type: 'compartment', map_id: 'endoplasmic_reticulum' },
            query: { dim: '2d', panel: '1', g1: 'skin 1', g2: 'testis', coords: '-7222.7,-4501.6,0.97,0,0,0' } },
          icon: 'tasks' },
        { title: 'GEM Repository',
          text: 'Over 350 GEMs can be downloaded from the <b>GEM Repository</b> or directly from the <b>Metabolic Atlas FTP server</b>. The tabular view enables customized selection.<br><br>Clicking on each of the models brings up more information about the model, including a text description and, if available, references. For support, the original authors should be contacted.',
          img: require('../assets/gems.jpg'),
          cardLink: 'GEM Repository',
          route: { name: 'gems' },
          icon: 'files-o' },
        { title: 'Export',
          text: '<b>Metabolic Atlas</b> provides open access to the models and associated annotations. Most of the data provided on the website is convenient to export, for example via <b>Export to TSV</b> buttons.<br><br>For the ones interested in extracting data in JSON format, we have documented our API. When using images or files obtained from our website, use the following reference:<br><br><a href="https://doi.org/10.1126/scisignal.aaz1482" target="_blank">Robinson, J., et al, 2020. <i>An atlas of human metabolism</i>. Sci. Signal. 13, eaaz1482 </a>',
          img: require('../assets/export.jpg'),
          cardLink: 'Export TSV for glyoxolate metabolites',
          route: { name: 'search', query: { term: 'glyoxalate' } },
          icon: 'download' },
        { title: 'Resources',
          text: 'Working with metabolic models requires a set of tools and external databases, which we have collected together for one-click access.<br><br>Additionally, Metabolic Atlas is open to further integrations.',
          img: require('../assets/resources.jpg'),
          cardLink: 'Resources',
          route: { name: 'resources' },
          icon: 'gears' },
        { title: 'Community',
          text: '<p>We are grateful for the efforts of scientists all over the world in creating the knowledge required to assemble high quality genome scale metabolic models. We are passionate about continuing on this journey of open curation of models.<br><br>We invite you to explore the world of GEMs through Metabolic Atlas, and hope it will enhance your interest in this field. We wish to continuously improve Metabolic Atlas for the community. Email us with any feedback, suggestions, or requests at <a href="mailto:">contact [at] metabolicatlas [dot] org</a>.</p>',
          img: require('../assets/resources.jpg'),
          cardLink: 'Contact us',
          route: { name: 'team' },
          icon: 'users' },
      ],
      news: [
        { date: '2020.04.27',
          hash: '27-April-2020',
          text: 'Metabolic Atlas v1.7 brings Map Viewer improvements' },
        { date: '2020.03.23',
          hash: '23-March-2020',
          text: 'Metabolic Atlas v1.6' },
        { date: '2020.02.07',
          hash: '7-February-2020',
          text: 'Metabolic Atlas v1.5 updates both integrated models' },
        { date: '2019.09.11',
          hash: '11-September-2019',
          text: 'Metabolic Atlas was presented in a course given by NBIS' },
        { date: '2019.09.05',
          hash: '5-September-2019',
          text: 'Metabolic Atlas v1.4 enables gene expression comparison' },
        { date: '2019.08.01',
          hash: '1-August-2019',
          text: 'Metabolic Atlas v1.3' },
        { date: '2019.06.25',
          hash: '25-June-2019',
          text: 'Metabolic Atlas is upgraded to v1.2 with Human-GEM updated to v1.1' },
        { date: '2019.05.29',
          hash: '29-May-2019',
          text: 'Metabolic Atlas is upgraded to v1.1' },
        { date: '2019.05.17',
          hash: '17-May-2019',
          text: 'Metabolic Atlas is publicly available as v1.0' },
      ],
    };
  },
  beforeMount() {
    this.currentMenu = this.menu[0]; // eslint-disable-line prefer-destructuring
  },
};

</script>
<style lang="scss">
#home .stripe:nth-child(2n) {
  background: whitesmoke;
  .columns {
    flex-direction: row-reverse;
  }
}
</style>
