<template>
  <!-- eslint-disable max-len -->
  <section class="section extended-section">
    <div class="container is-fullhd">
      <h3 class="title is-3">Metabolic Atlas</h3>
      <div class="columns is-variable is-8">
        <div class="column is-half has-text-justified">
          <div class="box is-hidden-tablet">
            <p class="subtitle has-text-weight-bold is-size-4 has-text-primary has-text-centered">Citing Metabolic Atlas</p>
            <a href="https://doi.org/10.1126/scisignal.aaz1482" target="_blank">Robinson, J., et al, 2020. <i>An atlas of human metabolism</i>. Sci. Signal. 13, eaaz1482 </a>
          </div>
          The Metabolic Atlas project is headed by <a href="https://www.sysbio.se/labs/nielsen" target="_new">Professor Jens Nielsen</a>, <a href="https://www.sysbio.se">Division of Systems and Synthetic Biology</a>, Department of Biology and Biological Engineering at the <a href="https://www.chalmers.se" target="_new">Chalmers University of Technology</a>. The platform is developed by members of <a href="https://www.chalmers.se/en/researchinfrastructure/csb/Pages/default.aspx">Computational Systems Biology Infrastructure</a> at Chalmers University of Technology and <a href="https://nbis.se" target="blank">National Bioinformatics Infrastructure Sweden</a>.<br><br>

          Metabolic Atlas is a freely available resource containing detailed information about a set of open-source  Genome-Scale Metabolic Models (GEMs), specifically <router-link :to="{ name: 'explorer', params: {model: 'Human-GEM'} }">Human-GEM</router-link> and <router-link :to="{ name: 'explorer', params: {model: 'Yeast-GEM'} }">Yeast-GEM</router-link>. These are two reference models containing all possible reactions that could occur in human, and yeast, respectively.<br><br>

          The research focus of the content of this website is <b>metabolism in a systems biology context</b>. The goal is to collect many curated GEMs, and to bring these models closer to <a href="https://en.wikipedia.org/wiki/FAIR_data" target="_new">FAIR principles</a>. To this end, the website also provides visualisations and comparisons of the GEMs, and links to <a href="resources">resources</a>: algorithms, other databases, and more general software applications (like RAVEN and PIANO).<br><br>

          Metabolic Atlas is intended to be used for applications in metabolomics, clinical chemistry, biomarker discovery and general education. In short, the vision is to create a one-stop-shop for everything metabolism related, starting with <a href="https://www.sysbio.se/labs/nielsen/#publications">the publications of the Nielsen lab</a>.<br><br>

          The development of Metabolic Atlas is led by <a href="https://nbis.se/about/staff/mihail-anton" target="_blank">Mihail Anton</a>, with team members Pierre-Etienne Cholley and Shan Huang. Past and more detailed contributions are <a href="https://github.com/SysBioChalmers/MetabolicAtlas/graphs/contributors" target="_blank">shown on GitHub</a>. For versions and release notes of the software behind Metabolic Atlas, <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases" target="_blank">check the GitHub page</a>. The integrated models are also available on GitHub, check our <router-link :to="{ name: 'gems' }">GEM Repository</router-link> for links to those.<br><br>

          <p>Metabolic Atlas would not be possible without the following excellent Elixir resources: <a href="https://proteinatlas.org" target="_blank">The Human Protein Atlas</a>, <a href="https://www.ensembl.org/" target="_blank">Ensembl</a>, <a href="https://www.uniprot.org" target="_blank">UniProt</a>, <a href="https://europepmc.org" target="_blank">Europe PMC</a>, <a href="https://identifiers.org" target="_blank">Identifiers.org</a>, <a href="https://www.ebi.ac.uk/chebi" target="_blank">ChEBi</a> and other essential sources of information: <a href="http://www.genome.jp/kegg/" target="_blank">KEGG: Kyoto Encyclopedia of Genes and Genomes</a>,  <a href="http://www.hmdb.ca/" target="_blank">The Human Metabolome Database</a>, <a href="https://www.metanetx.org" target="_blank">MetaNetX</a>, <a href="http://bigg.ucsd.edu" target="_blank">BiGG</a>, <a href="https://www.ncbi.nlm.nih.gov" target="_blank">NCBI</a>.
          </p>
        </div>
        <div class="column is-half has-text-justified content">
          <div class="box is-hidden-mobile">
            <p class="subtitle has-text-weight-bold is-size-4 has-text-primary has-text-centered">Citing Metabolic Atlas</p>
            <a href="https://doi.org/10.1126/scisignal.aaz1482" target="_blank">Robinson, J., et al, 2020. <i>An atlas of human metabolism</i>. Sci. Signal. 13, eaaz1482 </a>
          </div>
          <img width="100%" alt="The SysBio group 2019" src="../assets/group_19.jpg">
          <center>The SysBio group 2019</center>
          <br><br>
          <h4 class="title is-4">Scientific Advisors</h4>
          <nav id="advisors" class="level">
            <div v-for="advisor in advisors" :key="advisor.name" class="level-left">
              <a :href="advisor.url" target="_blank">
                <span class="level-item">
                  <figure class="image is-64x64">
                    <img class="is-rounded" :alt="advisor.name" :src="advisor.img" />
                  </figure>
                  {{ advisor.name }}
                </span>
              </a>
            </div>
          </nav>
          <br>
          <h4 class="title is-4">Contact</h4>
          <p>For any questions, comments or suggestions please email us at <a href="mailto:">contact [at] metabolicatlas [dot] org</a>.</p>
        </div>
      </div>
      <br>
      <h3 id="News" class="title is-3">News</h3>
      <div class="timeline is-centered">
        <header class="timeline-header">
          <span class="tag is-large has-text-primary has-text-weight-bold">today</span>
        </header>
        <template v-for="year in Object.keys(news).reverse()">
          <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
          <template v-for="newsItem in news[year]">
            <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
            <div :id="newsItem.date.replace(/ /g,'-')" class="timeline-item is-danger">
              <div class="timeline-marker is-primary" :class="{ 'is-icon' : newsItem.icon }">
                <i v-if="newsItem.icon" :class="`fa fa-${newsItem.icon}`"></i>
              </div>
              <div class="timeline-content">
                <p class="heading">{{ newsItem.date }}</p>
                <p v-html="newsItem.text"></p>
              </div>
            </div>
          </template>
          <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
          <header class="timeline-header">
            <span class="tag is-large has-text-primary has-text-weight-bold">{{ year }}</span>
          </header>
        </template>
      </div>
      <br><br>
      <div class="columns is-variable is-8">
        <div class="column has-text-justified content">
          <h3 id="privacy" class="title is-3">Privacy Notice</h3>
          <p>
            Metabolic Atlas gathers information about users solely to improve the usability and usefulness of the website. There are two types of cookies that are set by Metabolic Atlas: functionality cookies and tracking cookies.<br>
            Functionality cookies are used to personalize the appearence of the Metabolic Atlas.<br>
            Tracking cookies are used by our private analytics to track the users on our website. We use these to observe the anonymized behaviour on our website in order to improve it. We store partial IP, operating system, browser and browser language. This information is stored permanently for statistics and is not shared with any third party.<br>
            Additionally, we use the services of <a href="https://www.hotjar.com/" target="_blank">Hotjar</a>. This is an additional independent tracking service, which can produce a screen capture of the interactions on our website, including mouse movement. We use it for the purpose of figuring out how to improve our website, for example when the website interface is confusing. The data is stored for at most 3 months. Hotjar adheres to GDPR, <a href="https://www.hotjar.com/legal/compliance/gdpr-commitment" target="_blank">see more on their website</a>.<br>
            To opt out of any of these cookies, please set your browser to use the "DoNotTrack" header; doing this will disable the tracking. It is a good practice to enable this setting, here is how to do this for <a href="https://support.google.com/chrome/answer/2790761" target="_blank">Chrome</a> and <a href="https://support.mozilla.org/en-US/kb/how-do-i-turn-do-not-track-feature" target="_blank">Firefox</a> (in Safari this is enabled by default). Alternatively, see <a href="https://www.hotjar.com/legal/compliance/opt-out" target="_blank">Hotjar's instructions on their website</a>.<br>
            If you have any questions, please email us at <a href="mailto:">contact [at] metabolicatlas [dot] org</a>.
          </p>

          <h3 class="title is-3">Terms of Use</h3>
          <p>
            We do not guarantee the accuracy of any provided data, generated database, software or online service nor the suitability of databases, software and online services for any purpose.
            The content presented on Metabolic Atlas is contributed by members of the community who remain owners of said content.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'About',
  data() {
    return {
      news: {
        2020: [
          { date: '27 April 2020',
            text: '<b>Metabolic Atlas v1.7</b> is out. This release links the genes and metabolites directly to the maps, and improves the Map Viewer links to be more share-friendly. The overall appearance of the website has also been tweaked. More details can be found <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases/tag/1.7" target="_blank">on GitHub</a>.' },
          { date: '23 March 2020',
            text: '<b>Metabolic Atlas v1.6</b> is out. This release contains many user interface improvements, documentation updates and correction of typos. More details can be found <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases/tag/1.6" target="_blank">on GitHub</a>.' },
          { date: '7 February 2020',
            text: '<b>Metabolic Atlas v1.5</b> is out. This release updates the layout of the <i>Home</i>, <i>Explore</i>, and <i>Interaction Partner</i> pages. A <i>News</i> section has also been added on the <i>About</i> page. Other features include suggestions on the <i>Search</i> page, a contact button in the <i>GEM Browser</i>, and a progress bar at the top indicating page loading status. The Human-GEM has also been updated to v1.3, and the Yeast-GEM to v.8.3.4. More details can be found <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases/tag/1.5" target="_blank">on GitHub</a>.' },
        ],
        2019: [
          { date: '11 September 2019',
            text: '<b>Metabolic Atlas</b> was presented in the <a href="https://www.scilifelab.se/events/omics-integration-and-systems-biology/" target="_blank">Omics Integration and Systems Biology</a> course given by <a href="https://nbis.se" target="_blank">NBIS</a>.' },
          { date: '5 September 2019',
            text: '<b>Metabolic Atlas v1.4</b> is out. The main feature of this release is the <i>Data Overlay</i> panel on the <i>Map Viewer</i>, currently enabling data upload and comparison for gene expression. Other small tweaks on the <i>Map Viwewer</i> are: the fullscreen mode, hiding genes or subsystem highlights, some button layout changes. The RNA legend was refactored but maintains the same functionality. The <i>GEM Browser</i> tiles can be randomized by clicking a button. More details can be found <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases/tag/1.4" target="_blank">on GitHub</a>.' },
          { date: '1 August 2019',
            text: '<b>Metabolic Atlas v1.3</b> loads much faster. Across the website <i>enzyme</i> has been renamed to <i>gene</i>, and the <i>Global search</i> gives results in order, downloadable in TSV format. Among the minor tweaks are: notice on 404 page,  <i>Interaction partners</i> layout and <i>API</i> layout. More details can be found <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases/tag/1.3" target="_blank">on GitHub</a>.' },
          { date: '25 June 2019',
            text: '<b>Metabolic Atlas v1.2</b> adds more interaction on the 3D <i>Map Viewer</i>, and improves the <i>GEM Comparison</i> tables. It also contains several bug fixes. More details can be found in <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases/tag/1.2" target="_blank">on GitHub</a>. Moreover, <i>Human-GEM</i> was updated to v1.1.' },
          { date: '29 May 2019',
            text: '<b>Metabolic Atlas v1.1</b> has minor UI improvements, mainly around documentation, resources, <i>Interaction Partners</i> and <i>Map Viewe</i>, alongside deployment improvements with a focus on reducing downtime. More details can be found <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases/tag/1.1" target="_blank">on GitHub</a>.' },
          { date: '17 May 2019',
            text: '<b>Metabolic Atlas v1.0</b> is publicly available. We have finalized two main tools, the <i>GEM Browser</i> (including <i>Interaction Partners</i>) and <i>Map Viewer</i>. Additionally, Metabolic Atlas is hosting GEMs in a repository. More details can be found in <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases/tag/1.0" target="_blank">on GitHub</a>.',
            icon: 'flag' },
          { date: '2 May 2019',
            text: '<i>Human-GEM</i> is integrated, with complete compartment maps, and a significant number of the subsystem maps.' },
        ],
        2018: [
          { date: 'December 2018',
            text: 'New manually curated maps for <i>Human-GEM</i> are being created, and the MapViewer is faster when browsing these maps.' },
          { date: 'November 2018',
            text: 'Draft models of <i>Human-GEM</i> and <i>Yeast-GEM</i> have been integrated on the 23rd and 28th respectively.' },
          { date: 'September 2018',
            text: 'Development on Metabolic Atlas is coordinated by <a href="https://nbis.se/about/staff/mihail-anton" target="_blank">Mihail Anton</a> from <a href="https://nbis.se" target="blank">NBIS</a> in close collaboration with  <a href="https://www.sysbio.se">SysBio</a>, headed by <a href="https://www.sysbio.se/labs/nielsen" target="_new">Prof. Nielsen</a>.',
            icon: 'thumb-tack' },
        ],
        2017: [
          { date: 'September 2017',
            text: 'The project is coordinated by <a href="https://www.sysbio.se/labs/nielsen" target="_new">Prof. Nielsen</a>.',
            icon: 'thumb-tack' },
        ],
        2016: [
          { date: 'September 2016',
            text: 'The framework behind Metabolic Atlas is coordinated by Lena Hansson from <a href="https://nbis.se" target="blank">NBIS</a> in close collaboration with  <a href="https://www.sysbio.se">SysBio</a>, under the direction of <a href="https://www.sysbio.se/labs/nielsen" target="_new">Prof. Nielsen</a>.',
            icon: 'thumb-tack' },
          { date: 'March 2016',
            text: 'Work on a new Atlas began in the GitHub repository, directed by <a href="https://www.sysbio.se/labs/nielsen" target="_new">Prof. Nielsen</a>.',
            icon: 'thumb-tack' },
        ],
        2015: [
          { date: 'July 2015',
            text: 'A first Atlas focusing on human metabolism is made publicly available at <i>metabolicatlas.org</i>, with the associated publication <a href="https://academic.oup.com/database/article/doi/10.1093/database/bav068/2433201" target="_blank"><i>Human metabolic atlas: an online resource for human metabolism</i></a>.',
            icon: 'archive' },

        ],
      },
      /* eslint-disable global-require */
      advisors: [
        {
          name: 'Prof. Jens Nielsen',
          img: require('../assets/pic-jens.jpg'),
          url: 'https://www.sysbio.se/labs/nielsen/',
        }, {
          name: 'Dr. Jonathan Robinson',
          img: require('../assets/pic-jon.jpg'),
          url: 'https://nbis.se/about/staff/jonathan-robinson/',
        },
      ],
    };
  },
};
</script>

<style lang="scss">
#advisors{
  figure {
    margin: 0 1rem 0 0;
  }
  .level-item {
    justify-content: flex-start;
    margin: 0 4rem 0 0;
  }
}
</style>
