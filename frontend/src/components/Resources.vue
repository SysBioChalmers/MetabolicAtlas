<template>
  <div>
    <div>
      <div id="resources">
        <h2 class="title fc is-2">Tools</h2>
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
      <br>
      <div>
        <h2 class="title is-2">Databases</h2>
        <div v-for="db_data in databases">
          <div class="columns">
            <div class="column is-1">
              <a :href="db_data.link" target="_blank"><img :src="imgUrl(db_data.img)" height="75"></a>
            </div>
            <div class="column">
            <div class="dsc">
              <span>
                {{ db_data.description }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <br>
      <div>
        <h2 class="title is-2">API</h2>
        <div class="columns">
          <div class="column is-1">
            <a href="swagger">API</a>
          </div>
          <div class="column">
            <div class="dsc">
              <span>
                The set of URL requests for the <a href="metabolicatlas.org">metabolicatlas.org</a>
                that will return different .json files
                depending on the current request.
                Gives you the possibility of trying it out to see what the
                results would look like.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'resources',
  data() {
    return {
      tools: [
        { name: 'RAVEN',
          link: 'https://github.com/SysBioChalmers/RAVEN/',
          img: 'http://biomet-toolbox.chalmers.se/img/ravenLogo.png',
          description: '<b>RAVEN (Reconstruction, Analysis and Visualization of Metabolic Networks) Toolbox is a software suite that allows for semi-automated reconstruction of genome-scale models</b>. It makes use of published models and/or the KEGG database, coupled with extensive gap-filling and quality control features. <br>For more information please refer to <a href="http://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002980">Agren, R., Liu, L., Shoaie, S., Vongsangnak, W., Nookaew, I., Nielsen, J. (2013). <i>The RAVEN Toolbox and Its Use for Generating a Genome-scale Metabolic Model for Penicillium chrysogenum</i> PLOS Computational Biology</a>.' },
        { name: 'Gecko',
          link: 'https://github.com/SysBioChalmers/GECKO',
          img: 'https://github.com/SysBioChalmers/GECKO/raw/master/GECKO.png?raw=true',
          description: '<b>The GECKO toolbox is a Matlab/Python package for enhancing a Genome-scale model to account for Enzyme Constraints, using Kinetics and Omics</b>.' },
        { name: 'STIG-met',
          link: 'https://github.com/SysBioChalmers/STIG-met',
          img: '',
          description: '<b>Simulation Toolbox for Infant Growth with focus on Metabolism (STIG-met) is an integrated platform for simulation of human growth</b>. <br> We combine the experience from traditional growth models with GEMs to provide predictions of metabolic fluxes with enzyme level resolution on a day-to-day basis.<br>For using STIG-met, please refer to <a href="http://www.nature.com/articles/s41540-017-0004-5">Nilsson, A., Mardinoglu, A., and Nielsen, J. (2017).<i>Predicting growth of the healthy infant using a genome scale metabolic model.</i>Npj Systems Biology and Applications, 3(1), 3</a>' },
        { name: 'Kiwi',
          link: 'https://github.com/SysBioChalmers/Kiwi',
          img: 'https://pythonhosted.org/KiwiDist/_images/kiwi_logo.png',
          description: '<b>The Kiwi module combines geneset analyses with biological networks to visualize the interactions between genesets that are significant in a given biological system</b> such that the inherent connectivity between gene-sets becomes apparent, by visualize whether these entities or processes are isolated or connected by means of their biological interaction. <br>For more information please refer to <a href="https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-014-0408-9">V&auml;remo, L., Gatto, F., Nielsen, J. (2014). <i>Kiwi: a tool for integration and visualization of network topology and gene-set analysis</i> BMC Bioinformatics</a>.' },
      ],
      databases: [
        { name: 'YSeq Browser',
          link: 'http://www.sysbio.se/Yseq/',
          img: './YseqLogo.png',
          description: 'Genome and trascriptome (RNAseq and Microarray) browser of Saccharomyces cerevisiae.' },
        { name: 'yApoptosis',
          link: 'http://www.ycelldeath.com/yapoptosis/',
          img: './YAp_logo.gif',
          description: 'yApoptosis is an extensively-curated database dedicated for researchers working on yeast apoptosis. It is an open platform established to facilitate the organization and sharing of knowledge.' },
        { name: 'yStreX',
          link: 'http://www.ystrexdb.com/',
          img: './logo_ystrex.png',
          description: 'yStreX is an online database that collects, stores and distributes genome-wide expression data generated in the studies of stress responses using east Saccharomyces cerevisiae as the model organism.' },
        { name: 'HCSD',
          link: 'http://cancersecretome.org/',
          img: './HCSD_logo.png',
          description: 'The human cancer secretome database (HCSD) is a comprehensive database for human cancer secretome data.' },
      ],
      dBImageSources: null,
    };
  },
  methods: {
    imgUrl(path) {
      return this.dBImageSources(path);
    },
  },
  beforeMount() {
    this.dBImageSources = require.context('../assets', false, /\.(png|gif)$/);
  },
};

</script>

<style lang="scss">
#resources {
  .title {
    display: block;
    margin-bottom: 1.5rem;
    margin-top: 2rem;
  }

  .title.fc{
    margin-top: 0;
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
