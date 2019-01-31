<template>
  <section class="section extended-section">
    <div class="container" id="home">
      <div class="columns">
        <div class="column">
          <div class="card">
            <header class="card-header has-background-contrast has-text-centered" style="justify-content: center;">
              <p class="card-content title has-text-white">METABOLIC ATLAS - THE ATLAS FOR METABOLISM EXPLORATION</p>
            </header>
          </div>
        </div>
      </div>
      <div class="columns">
        <div class="column">
          <div class="card">
            <div class="columns is-mobile is-multiline margin-fix">
              <div class="column is-narrow is-full-mobile has-background-primary has-text-weight-bold is-paddingless">
                <aside class="menu">
                  <ul class="menu-list is-size-5">
                    <li v-for="menuItem in menu">
                      <a @click="selectMenu(menuItem)" :class="[ {'is-active' : menuItem.title === currentMenu.title}, menuItem.type]">{{ menuItem.title}}</a>
                    </li>
                  </ul>
                </aside>
              </div>
              <div class="column is-full-mobile more-padding">
                <p class="is-size-5" v-html="currentMenu.text"></p>
              </div>
              <div class="column is-full-mobile more-padding is-v-aligned">
                <div class="card has-text-centered">
                  <router-link :to="currentMenu.url"><img :src="currentMenu.img" /></router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div id="newsandcommunity" class="columns is-variable is-6">
        <div class="column is-half" v-for="card in cards">
          <div class="card is-size-5">
            <header class="card-header has-background-primary">
              <p class="card-content has-text-weight-bold has-text-white">{{ card.title }}</p>
            </header>
            <div class="card-content">
              <p v-html="card.text"></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
/* eslint-disable global-require*/
export default {
  name: 'home',
  data() {
    return {
      menu: [
        { type: '',
          title: 'Welcome',
          text: '<b>Metabolic Atlas</b> is a hub for genome scale metabolic models (GEMs): it integrates open-source consensus models for easy and visual browsing and analysis; also, it provides access to raw model files.<br><br>Citation goes here.',
          img: require('../assets/logo.png'),
          url: '/about' },
        { type: '',
          title: 'Explore integrated models',
          text: 'After careful consideration, open-source consensus models are integrated into the <b>Metabolic Atlas</b>. This manual process ensures the presented models are of the highest standard, and have the required visual components. Also, it gives us the possibility to integrate with other databases, such as the <a href="https://proteinatlas.org" target=_blank>Human Protein Atlas</a>.',
          img: require('../assets/explorer.jpg'),
          url: '/explore' },
        { type: 'homepage-submenu',
          title: 'GEM Browser',
          text: 'The integrated models are stored in a database, for powerful query and exploration.',
          img: require('../assets/gemBrowser2.png'),
          url: '/explore' },
        { type: 'homepage-submenu',
          title: 'Map Viewer',
          text: 'For each of the integrated models, <b>Metabolic Atlas</b> can automatically generate 3D maps. The manually curated maps of the <i>human-GEM</i> are also made available, at both compartment and subsystem level.',
          img: require('../assets/mapViewer2.png'),
          url: '/explore' },
        { type: 'homepage-submenu',
          title: 'Search',
          text: 'Search works either within the slected integrated model or across all models.',
          img: require('../assets/search.jpg'),
          url: '/explore/search' },
        { type: 'homepage-submenu',
          title: 'Export',
          text: 'We believe in openness: everything presented on the website can be exported, often in multiple formats.',
          img: '',
          url: '' },
        { type: '',
          title: 'Community GEMs',
          text: 'Some genome scale metabolic models have still to grow to the point where they can be integrated into <b>Metabolic Atlas</b>. Until then, we provide the tools to decide which of them is of interest, and ways to download it.',
          img: require('../assets/gems.jpg'),
          url: '/gems' },
        { type: 'homepage-submenu',
          title: 'Compare',
          text: 'Before deciding on which GEM to download, use the <i>Compare</i> feature to see how different models overlap.<br><br>This feature is still undergoing significant development.',
          img: require('../assets/compare.jpg'),
          url: '/compare' },
        { type: 'homepage-submenu',
          title: 'Analyze',
          text: 'This feature is still undergoing significant development.',
          img: '',
          url: '' },
        { type: 'homepage-submenu',
          title: 'Download',
          text: 'The community GEMs can be downloaded from the browser or via the <b>Metabolic Atlas</b> FTP server.',
          img: require('../assets/download.jpg'),
          url: '/gems/download' },
        { type: '',
          title: 'Resources',
          text: 'Working with metabolic models requires a set of tools and external databases, which we have collected for one-click access.<br>The <b>Metabolic Atlas</b> database is open to further integrations via the API.',
          // img: require('../assets/resources.jpg'),
          url: '/resources' },
      ],
      currentMenu: {},
      cards: [
        { title: 'Latest news',
          text: '<p> 17.12.2018 MapViewer is speedier at browsing manually curated maps <br> 08.12.2018 New maps for <i>Human1</i> are being created <br> 28.11.2018 <i>Human1</i> is now integrated <br> 23.11.2018 <i>Yeast8</i> is now integrated </p>' },
        { title: 'Community',
          text: '<p>One should try to not underestimate the effort put in by scientists all over the world into creating all the knowledge required to assemble high quality genome scale metabolic models. We are grateful to all of them, and are passionate about continuing on this journey of open curation of models.<br>On this note, we would like to invite you to discover the world of GEMs through Metabolic Atlas, hoping this will enhance your interest in this field.</p>' },
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
