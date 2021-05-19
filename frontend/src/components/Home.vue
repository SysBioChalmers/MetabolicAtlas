<template>
  <div class="extended-section">
    <section class="hero is-primary is-bold py-6">
      <router-link :to="{ name: 'explorer', params: { model: 'Human-GEM' } }">
        <div class="hero-body has-text-centered">
          <p class="is-size-1 title">METABOLIC ATLAS </p>
          <p class="is-size-5">
            open source genome-scale metabolic models for easy browsing and analysis
          </p>
        </div>
      </router-link>
    </section>

    <section id="home">

      <div class="py-6">
        <div class="container px-6">
          <div class="columns is-multiline is-mobile is-variable is-8-tablet is-centered is-vcentered">
            <div v-for="item in tools" :key="item.title" class="column is-3-desktop is-6-mobile is-size-5">
              <router-link :to="item.route">
                <div class="card hoverable">
                  <div class="card-image">
                    <figure class="image is-4by3">
                      <img :src="item.img" :alt="item.title" />
                    </figure>
                  </div>
                  <footer class="card-footer has-text-centered">
                    <a class="card-footer-item has-text-weight-bold is-size-4 is-size-5-mobile">
                      {{ item.cardLink }}
                    </a>
                  </footer>
                </div>
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <div class="has-background-white-ter py-6">
        <div class="container px-6">
          <p class="title is-size-4 has-text-centered pt-4">
            <router-link :to="news.route" class="has-text-primary">
              <span class="icon is-large fa-lg">
                <i :class="`fa fa-${news.icon}`"></i>
              </span>
              {{ news. title }}
            </router-link>
          </p>
          <div class="columns is-variable is-8 pt-3">
            <div class="column is-6 is-size-5">
              <p>The main versions of <b>Metabolic Atlas</b> are associated with scientific articles as follows.</p><br>
              <div class="box">
                <p>Version 2.0:
                  <i>Genome-scale reconstruction of metabolic networks of model animals
                    represents a platform for translational research</i>.
                  Article under consideration.
                </p>
              </div>
              <div class="box">
                <p>Version 1.0: <a href="https://doi.org/10.1126/scisignal.aaz1482" target="_blank">Robinson, J., et al, 2020. <i>An atlas of human metabolism</i>. Sci. Signal. 13, eaaz1482</a></p>
              </div>
            </div>
            <div class="column is-6 is-size-5">
              <p v-html="news.text"></p>
              <table>
                <template v-for="el in newsItems">
                  <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                  <tr v-if="el.date">
                    <td>{{ el.date }}</td>
                    <td class="pl-3">
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

      <div class="py-6">
        <div class="container px-6 pt-6">
          <!-- eslint-disable -->
          <div v-for="features in [features1, features2]" class="columns is-variable is-8">
            <div v-for="item in features" :key="item.title" class="column is-6 is-size-5">
              <p class="title is-size-4">
                <router-link :to="item.route" class="has-text-primary">
                  <span class="icon is-large fa-lg">
                    <i :class="`fa fa-${item.icon}`"></i>
                  </span>
                  {{ item. title }}
                </router-link>
              </p>
              <div class="columns pb-6">
                <div class="column is-7 px-3">
                  <p v-html="item.text"></p>
                </div>
                <div class="column is-offset-1-mobile is-10-mobile">
                  <router-link :to="item.route">
                    <div class="card hoverable">
                      <div class="card-image">
                        <figure class="image is-4by3">
                          <img class="hoverable" :src="item.img" :alt="item.title" />
                        </figure>
                      </div>
                    </div>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="has-background-white-ter py-6">
        <div class="container px-6">
          <div class="columns is-variable is-8 is-vcentered py-6">
            <div class="column is-offset-1 is-5 is-size-5">
              <p class="title is-size-4 has-text-centered">
                <router-link :to="repository.route" class="has-text-primary">
                  <span class="icon is-large fa-lg">
                    <i :class="`fa fa-${repository.icon}`"></i>
                  </span>
                  {{ repository. title }}
                </router-link>
              </p>
              <p v-html="repository.text"></p>
            </div>
            <div class="column is-5 is-offset-1-mobile is-10-mobile">
              <router-link :to="repository.route">
                <div class="card hoverable">
                  <div class="card-image">
                    <figure class="image is-4by3">
                      <img :src="repository.img" :alt="repository.title" />
                    </figure>
                  </div>
                </div>
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <div class="py-6">
        <div class="container px-6">
          <div class="columns is-variable is-8">
            <div v-for="item in comRes" :key="item.title" class="column is-6 is-size-5 py-6">
              <p class="title is-size-4">
                <router-link :to="item.route" class="has-text-primary">
                  <span class="icon is-large fa-lg">
                    <i :class="`fa fa-${item.icon}`"></i>
                  </span>
                  {{ item. title }}
                </router-link>
              </p>
              <p v-html="item.text"></p>
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
      news: {
        title: "What's new",
        text: '',
        img: require('../assets/gemBrowser.jpg'),
        route: { name: 'about', hash: '#News' },
        icon: 'newspaper-o',
      },
      tools: [
        { title: messages.gemBrowserName,
          text: 'The <b>GEM Browser</b> enables powerful query and exploration of model content in tabular format.<br><br>A wide range of attributes, including reaction equations, metabolite formulas, gene rules and subsystem contents, are presented as a detailed network of individual model components. They are highly interconnected and rationally associated to easily navigate and switch between them.<br><br>Visit the documentation to learn about the different functionalities provided by the GEM Browser.',
          img: require('../assets/gemBrowser.jpg'),
          cardLink: 'GEM Browser',
          route: { name: 'browser', params: { model: 'Human-GEM' } },
          icon: 'table' },
        { title: messages.mapViewerName,
          text: 'For easy visualization, <b>Metabolic Atlas</b> handles both 2D and 3D maps. For each of the integrated models, the website automatically generates 3D graphs at both compartment and subsystem level.<br><br>Both compartment and subsystem 2D maps of the Human-GEM have been created by Human-GEM contributors and are manually curated. On these maps, one can search for reactions, metabolites or genes. Moreover, RNA expression data from Human Protein Atlas can be overlaid.<br><br>By clicking on an element on the map, more information of that element will be shown on the left sidebar. From there, one can navigate back to the <b>GEM Browser</b> for detailed information.',
          img: require('../assets/mapViewer.jpg'),
          cardLink: 'Map Viewer',
          route: { name: 'viewer',
            params: { model: 'Human-GEM', type: 'compartment', map_id: 'golgi_apparatus' },
            query: { dim: '2d' } },
          icon: 'map-o' },
        { title: messages.interPartName,
          text: `The <b>Interaction Partners</b> graph shows connectivity between metabolites and genes based on their associated reactions.<br><br>The graph is dynamically generated and is customizable. One can interact with a restricted part of the metabolic network, or further expand the interaction partners of any element already on the graph. Moreover, RNA expression data from the Human Protein Atlas can be overlaid onto the graph. <br><br>This feature is available only for metabolites and genes, and is accessible via the <b>${messages.gemBrowserName}</b>.`,
          img: require('../assets/interaction.jpg'),
          cardLink: 'Interaction Partners',
          route: { name: 'interaction', params: { model: 'Human-GEM' } },
          icon: 'connectdevelop' },
      ],
      features1: [
        { title: 'Search',
          text: 'The menu bar contains a shortcut to the <b>Global search</b> function, which enables users to easily search cellular components across all the integrated models available for further filtering.',
          img: require('../assets/search.jpg'),
          route: { name: 'search', query: { term: '' } },
          icon: 'search' },
        { title: 'Analyze',
          text: 'Gene expression data from the Human Protein Atlas can be viewed in the 2D and 3D maps and Interaction Partners. User data can also be overlaid onto the maps, with the option of comparing datasets, for example against normal tissue. Additional types of omics integrations are under development.',
          img: require('../assets/analyze.jpg'),
          route: { name: 'viewer',
            params: { model: 'Human-GEM', type: 'compartment', map_id: 'endoplasmic_reticulum' },
            query: { dim: '2d', panel: '1', g1: 'skin 1', g2: 'testis', coords: '-7222.7,-4501.6,0.97,0,0,0' } },
          icon: 'tasks' },
      ],
      features2: [
        { title: 'Export',
          text: 'Most of the data provided on the website is convenient to export, for example via <b>Export to TSV</b> buttons. For the extracting data in JSON format, we have documented our API.',
          img: require('../assets/export.jpg'),
          route: { name: 'search', query: { term: 'glyoxalate' } },
          icon: 'download' },
        { title: 'Compare',
          text: 'The integrated models can be compared on-the-fly via the external identifiers they share. Moreover, a 3-way comparison can be performed as well.',
          img: require('../assets/comparison.jpg'),
          route: { name: 'comparemodels' },
          icon: 'download' },
      ],
      repository: {
        title: 'GEM Repository',
        text: 'Over 350 GEMs can be downloaded from the <b>GEM Repository</b> or directly from the <b>Metabolic Atlas FTP server</b>. The tabular view enables customized selection.<br><br>Clicking on each of the models brings up more information about the model, including a text description and, if available, references. For support, the original authors should be contacted.',
        img: require('../assets/gems.jpg'),
        route: { name: 'gems' },
        icon: 'files-o',
      },
      comRes: [
        { title: 'Resources',
          text: 'Working with metabolic models requires a set of tools and external databases, which we have collected together for one-click access.<br><br>Additionally, Metabolic Atlas is open to further integrations.',
          route: { name: 'resources' },
          icon: 'gears' },
        { title: 'Community',
          text: '<p>We are grateful for the efforts of scientists all over the world in creating the knowledge required to assemble high quality genome scale metabolic models. We are passionate about continuing on this journey of open curation of models.<br><br>We invite you to explore the world of GEMs through Metabolic Atlas, and hope it will enhance your interest in this field. We wish to continuously improve Metabolic Atlas for the community. Email us with any feedback, suggestions, or requests at <a href="mailto:">contact [at] metabolicatlas [dot] org</a>.</p>',
          route: { name: 'about' },
          icon: 'users' },
      ],
      newsItems: [
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
};

</script>
<style lang="scss">
#home {
  .card {
    max-width: 500px;
  }
  .stripe:nth-child(2n) {
    background: whitesmoke;
    .columns {
      flex-direction: row-reverse;
    }
  }
}
</style>
