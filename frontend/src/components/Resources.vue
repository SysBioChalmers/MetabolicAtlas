<template>
  <div>
    <div>
      <div>
        <span class="title">Tools</span>
        <div v-for="tool_data in tools">
          <div class="columns">
            <div class="column is-1">
              <a v-if="tool_data.img" :href="tool_data.link" target="_blank">
                <img  :src="tool_data.img" width="150">
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
        <span class="title">Databases</span>
        <div v-for="db_data in databases">
          <div class="columns">
            <div class="column is-1">
              <a :href="db_data.link" target="_blank"><img :src="db_data.img"></a>
            </div>
            <div class="column">
              {{ db_data.description }}
            </div>
          </div>
        </div>
      </div>
      <br>
      <div>
        <span class="title">Api</span>
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
          img: './assets/YseqLogo.png',
          description: 'Genome and trascriptome (RNAseq and Microarray) browser of Saccharomyces cerevisiae.' },
        { name: 'yApoptosis',
          link: 'http://www.ycelldeath.com/yapoptosis/',
          img: '../assets/YAp_logo.gif',
          description: 'yApoptosis is an extensively-curated database dedicated for researchers working on yeast apoptosis. It is an open platform established to facilitate the organization and sharing of knowledge.' },
        { name: 'yStreX',
          link: 'http://www.ystrexdb.com/',
          img: '../assets/logo_ystrex.png',
          description: 'yStreX is an online database that collects, stores and distributes genome-wide expression data generated in the studies of stress responses using east Saccharomyces cerevisiae as the model organism.' },
        { name: 'HCSD',
          link: 'http://cancersecretome.org/',
          img: '../assets/HCSD_logo.png',
          description: 'The human cancer secretome database (HCSD) is a comprehensive database for human cancer secretome data.' },
      ],
    };
  },
  methods: {
  },
};

</script>

<style lang="scss">

.title {
  display: block;
  margin-bottom: 1rem;
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

</style>
