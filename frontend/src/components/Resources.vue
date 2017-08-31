<template>
  <div>
    <div>
      <div id="resources">
        <h2 class="title fc is-2">Tools</h2>
        <div v-for="tool_data in tools">
          <div class="columns">
            <div class="column is-1">
              <a v-if="tool_data.img" :href="tool_data.link" target="_blank">
                <img :src="tool_data.img" width="150">
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
                {{ tool_data.description }}
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
        <h2 class="title is-2">Api</h2>
          <a href="swagger">Swagger API</a>
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
          img: '',
          description: 'RAVEN (Reconstruction, Analysis and Visualization of Metabolic Networks) Toolbox is a software suite that allows for semi-automated reconstruction of genome-scale models. It makes use of published models and/or the KEGG database, coupled with extensive gap-filling and quality control features.' },
        { name: 'Gecko',
          link: 'https://github.com/SysBioChalmers/GECKO',
          img: 'https://github.com/SysBioChalmers/GECKO/raw/master/GECKO.png?raw=true',
          description: 'The GECKO toolbox is a Matlab/Python package for enhancing a Genome-scale model to account for Enzyme Constraints, using Kinetics and Omics.' },
        { name: 'STIG-met',
          link: 'https://github.com/SysBioChalmers/STIG-met',
          img: '',
          description: 'Simulation Toolbox for Infant Growth with focus on Metabolism.' },
        { name: 'Kiwi',
          link: 'https://github.com/SysBioChalmers/Kiwi',
          img: 'https://pythonhosted.org/KiwiDist/_images/kiwi_logo.png',
          description: 'The Kiwi module combines geneset analyses with biological networks to visualize the interactions between genesets that are significant in a given biological system.' },
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
    height: 75px;
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
