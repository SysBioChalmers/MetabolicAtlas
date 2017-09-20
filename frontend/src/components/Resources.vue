<template>
  <div id="resources">
    <div>
      <a href="#tools">Tools</a> 
      <a href="#databases">Databases</a> 
      <a href="#api">API</a> 
      <a href="#additional">Additional Resources</a>
    </div>
    <div class="rsection">
      <h2 id="tools" class="title is-2">Tools</h2>
      <div v-for="tool_data in tools">
        <div class="columns">
          <div class="column is-1">
            <a v-if="tool_data.img" :href="tool_data.link" target="_blank">
              <img :src="tool_data.img" width="160">
            </a>
            <a v-else :href="tool_data.link" target="_blank">
              <div class="name">
                <span>{{ tool_data.name }}</span>
              </div>
            </a>
          </div>
          <div class="column">
            <div class="dsc">
              <span>
                <div v-html="tool_data.description"></div>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="rsection">
      <h2 id="databases" class="title is-2">Databases</h2>
      <div v-for="db_data in databases">
        <div class="columns">
          <div class="column is-1">
            <a :href="db_data.link" target="_blank"><img :src="imgUrl(db_data.img)" height="75"></a>
          </div>
          <div class="column">
            <div class="">
              <span>
                <div v-html="db_data.description"></div>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="rsection">
      <h2 id="api" class="title is-2">API</h2>
      <div class="columns">
        <div class="column is-1">
          <a href="swagger">GEM API</a>
        </div>
        <div class="column">
          <div class="">
            <span>
              The set of URL requests for the <a href="metabolicatlas.org">metabolicatlas.org</a>
              that will return different .json files
              depending on the current request.
              Gives you the possibility of trying it out to see what the
              results would look like.
              Main focus on the data available in the GEMs.
            </span>
          </div>
        </div>
      </div>
    </div>
    <div class="rsection">
      <h2 id="additional" class="title is-2">Additional resources</h2>
      <div class="columns">
        <div class="column is-1">
          <a href="hreed">Hreed</a>
        </div>
        <div class="column">
          <div class="">
            <span>
              Hreed (Human REaction Entities Database) facilitates an access
              to the Hreed reaction data, which can be easily retrieved by
              using specific keywords or names of related genes, proteins, compounds and cross-references.
            </span>
          </div>
        </div>
      </div>
      <div class="columns">
        <div class="column is-1">
          <a href="atlas">Atlas</a>
        </div>
        <div class="column">
          <div class="">
            <span>
              Atlas web interface can be used for visualization of the GEMs
              collection overlaid on KEGG metabolic pathway maps with a zoom/pan user interface.
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import $ from 'jquery';

export default {
  name: 'resources',
  data() {
    return {
      tools: [
        { name: 'STIG-met',
          link: 'https://github.com/SysBioChalmers/STIG-met',
          img: '',
          year: '2017',
          description: '<b>Simulation Toolbox for Infant Growth with focus on Metabolism (STIG-met) is an integrated platform for simulation of human growth</b>. <br> We combine the experience from traditional growth models with GEMs to provide predictions of metabolic fluxes with enzyme level resolution on a day-to-day basis.<br>For more information please refer to <a href="http://www.nature.com/articles/s41540-017-0004-5">Nilsson, A., Mardinoglu, A., and Nielsen, J. (2017).<i>Predicting growth of the healthy infant using a genome scale metabolic model.</i> Npj Systems Biology and Applications, 3(1), 3</a>',
          PMID: '28649430' },
        { name: 'Gecko',
          link: 'https://github.com/SysBioChalmers/GECKO',
          img: 'https://github.com/SysBioChalmers/GECKO/raw/master/GECKO.png?raw=true',
          year: '-',
          description: '<b>GECKO is a Matlab/Python package for enhancing Genome-scale metabolic models (GEMs) with Enzyme Constraints, using Kinetics and Omics</b>. With it we can improve simulation performance of GEMs, reduce flux variability and get insight into enzyme usage.<br> Additional information about GECKO can be found in the following publication: <a href="">Sánchez, B., Zhang, C., Nilsson, A., Lahtvee, P., Kerkhoven, E., Nielsen, J. (2017). <i>Improving the phenotype predictions of a yeast genome-scale metabolic model by incorporating enzymatic constraints</i>. Molecular Systems Biology, 13(8): 935</a>' },
        { name: 'Kiwi',
          link: 'https://github.com/SysBioChalmers/Kiwi',
          img: 'https://pythonhosted.org/KiwiDist/_images/kiwi_logo.png',
          year: '2014',
          description: '<b>The Kiwi module combines geneset analyses with biological networks to visualize the interactions between genesets that are significant in a given biological system</b> such that the inherent connectivity between gene-sets becomes apparent, by visualize whether these entities or processes are isolated or connected by means of their biological interaction. <br>For more information please refer to <a href="https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-014-0408-9">V&auml;remo, L., Gatto, F., Nielsen, J. (2014). <i>Kiwi: a tool for integration and visualization of network topology and gene-set analysis</i> BMC Bioinformatics</a>.',
          PMID: '25496126' },
        { name: 'Piano',
          link: 'https://varemo.github.io/piano/',
          img: 'https://varemo.github.io/piano/loggo.png',
          year: '2013',
          description: '<b>Platform for integrative analysis of omics data</b> (PIANO) is an An R/Bioconductor package for gene set analysis. <br> For more information please refer to <a href="https://academic.oup.com/nar/article-lookup/doi/10.1093/nar/gkt111">V&auml;remo, L., Nielsen, J., Nookaew, I. (2013). <i>Enriching the gene set analysis of genome-wide data by incorporating directionality of gene expression and combining statistical hypotheses and methods</i> NAR</a>.',
          PMID: '23444143' },
        { name: 'RAVEN',
          link: 'https://github.com/SysBioChalmers/RAVEN/',
          img: 'http://biomet-toolbox.chalmers.se/img/ravenLogo.png',
          year: '2013',
          description: '<b>RAVEN (Reconstruction, Analysis and Visualization of Metabolic Networks) Toolbox is a software suite that allows for semi-automated reconstruction of genome-scale models</b>. It makes use of published models and/or the KEGG database, coupled with extensive gap-filling and quality control features. <br>For more information please refer to <a href="http://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002980">Agren, R., Liu, L., Shoaie, S., Vongsangnak, W., Nookaew, I., Nielsen, J. (2013). <i>The RAVEN Toolbox and Its Use for Generating a Genome-scale Metabolic Model for Penicillium chrysogenum</i>. PLOS Computational Biology</a>.',
          PMID: '23555215' },
      ],
      databases: [
        { name: 'YSeq Browser',
          link: 'http://www.sysbio.se/Yseq/',
          img: './YseqLogo.png',
          description: '<b>Genome and trascriptome (RNAseq and Microarray) browser of <i>Saccharomyces cerevisiae</i></b>.' },
        { name: 'yApoptosis',
          link: 'http://www.ycelldeath.com/yapoptosis/',
          img: './YAp_logo.gif',
          description: '<b>yApoptosis is an extensively-curated database dedicated for researchers working on yeast apoptosis</b>. It is an open platform established to facilitate the organization and sharing of knowledge.' },
        { name: 'yStreX',
          link: 'http://www.ystrexdb.com/',
          img: './logo_ystrex.png',
          description: '<b>yStreX is an online database that collects, stores and distributes genome-wide expression data generated in the studies of stress responses using yeast <i>Saccharomyces cerevisiae</i> as the model organism</b>.' },
        { name: 'HCSD',
          link: 'http://cancersecretome.org/',
          img: './HCSD_logo.png',
          description: '<b>The human cancer secretome database (HCSD) is a comprehensive database for human cancer secretome data</b>. Query, and compare, publicly available proteomics data published in the field of cancer secretome and tumor microenviroment, and visualize the predicted secretory features and post-translational modification sites (PTMs) for each protein. <br>For more information please refer to <a href="">Feizi, A., Banaei-Esfahani, A., Nielsen, J. (2015) <i>HCSD: the human cancer secretome database</i>. Database 2015 ' },
      ],
      dBImageSources: null,
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.$route.hash) {
        this.scrollToHash(this.$route.hash);
      }
    },
  },
  methods: {
    imgUrl(path) {
      return this.dBImageSources(path);
    },
    scrollToHash(hash) {
      $(window).scrollTop($(hash).offset().top);
    },
  },
  beforeMount() {
    this.dBImageSources = require.context('../assets', false, /\.(png|gif)$/);
  },
  mounted() {
    if (this.$route.hash) {
      this.scrollToHash(this.$route.hash);
    }
  },
};

</script>

<style lang="scss">
#resources {
  .rsection {
    display: block;
    margin-bottom: 1.5rem;
    margin-top: 2rem;
  }

  .dsc, .name {
    height: 100px;
    line-height: 75px;

    span {
      display: inline-block;
      vertical-align: middle;
      line-height: normal;
    }
  }

  .name {
    font-size: 1.5rem;
  }
}

</style>
