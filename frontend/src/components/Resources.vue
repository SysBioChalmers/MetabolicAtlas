<template>
  <section class="section extended-section">
    <div class="container is-fullhd">
      <template v-for="(elems, category) in resources">
        <!-- eslint-disable-next-line vue/require-v-for-key -->
        <div class="columns">
          <div class="column is-offset-2 has-text-centered-mobile">
            <h3 class="title is-3">{{ category }}</h3>
          </div>
        </div>
        <div v-for="elem in elems" :key="elem.name" class="columns">
          <br>
          <div class="column is-2 has-text-centered">
            <a :href="elem.link" target="_blank">
              <template v-if="elem.img">
                <img :src="elem.img" />
              </template>
              <template v-else>
                <h4 class="has-text-centered title is-4">{{ elem.name }}</h4>
              </template>
            </a>
          </div>
          <div class="column has-text-justified">
            <a :href="elem.link" target="_blank"><b>{{ elem.title }}</b></a><br>
            {{ elem.description }}<br>
            <a :href="elem.citation_url" target="_blank" v-html="elem.citation"></a>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<script>

/* eslint-disable global-require */
export default {
  name: 'Resources',
  data() {
    return {
      resources: {
        Tools: [
          { name: 'STIG-met',
            link: 'https://github.com/SysBioChalmers/STIG-met',
            img: '',
            title: 'Simulation Toolbox for Infant Growth with focus on Metabolism (STIG-met) is an integrated platform for simulation of human growth',
            description: 'We combine the experience from traditional growth models with GEMs to provide predictions of metabolic fluxes with enzyme level resolution on a day-to-day basis.',
            citation: 'Nilsson, A., Mardinoglu, A., and Nielsen, J. (2017). <i>Predicting growth of the healthy infant using a genome scale metabolic model.</i> Npj Systems Biology and Applications, 3(1), 3',
            citation_url: 'http://www.nature.com/articles/s41540-017-0004-5' },
          { name: 'Gecko',
            link: 'https://github.com/SysBioChalmers/GECKO',
            img: require('../assets/gecko-logo.png'),
            title: 'GECKO is a Matlab/Python package for enhancing Genome-scale metabolic models (GEMs) with Enzyme Constraints, using Kinetics and Omics',
            description: 'With it we can improve simulation performance of GEMs, reduce flux variability and get insight into enzyme usage.',
            citation: 'Sánchez, B., Zhang, C., Nilsson, A., Lahtvee, P., Kerkhoven, E., Nielsen, J. (2017). <i>Improving the phenotype predictions of a yeast genome-scale metabolic model by incorporating enzymatic constraints</i>. Molecular Systems Biology, 13(8): 935',
            citation_url: 'http://msb.embopress.org/content/13/8/935' },
          { name: 'Kiwi',
            link: 'https://github.com/SysBioChalmers/Kiwi',
            img: require('../assets/kiwi-logo.png'),
            title: 'The Kiwi module combines geneset analyses with biological networks to visualize the interactions between genesets that are significant in a given biological system',
            description: 'With Kiwi, the inherent connectivity between gene-sets becomes apparent - one can visualize whether these entities or processes are isolated or connected by means of their biological interaction.',
            citation: 'V&auml;remo, L., Gatto, F., Nielsen, J. (2014). <i>Kiwi: a tool for integration and visualization of network topology and gene-set analysis</i>. BMC Bioinformatics',
            citation_url: 'https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-014-0408-9' },
          { name: 'Piano',
            link: 'https://varemo.github.io/piano/',
            img: require('../assets/piano-logo.jpg'),
            title: 'Platform for integrative analysis of omics data (PIANO) is an An R/Bioconductor package for gene set analysis',
            description: 'Gene set analysis (GSA) is used to elucidate genome-wide data, in particular transcriptome data. We have developed the R package Piano that collects a range of GSA methods into the same system, for the benefit of the end-user. Further on we refine the GSA workflow by using modifications of the gene-level statistics. This enables us to divide the resulting gene set P -values into three classes, describing different aspects of gene expression directionality at gene set level.',
            citation: 'V&auml;remo, L., Nielsen, J., Nookaew, I. (2013). <i>Enriching the gene set analysis of genome-wide data by incorporating directionality of gene expression and combining statistical hypotheses and methods</i>. NAR',
            citation_url: 'https://academic.oup.com/nar/article-lookup/doi/10.1093/nar/gkt111' },
          { name: 'RAVEN',
            link: 'https://github.com/SysBioChalmers/RAVEN/',
            img: require('../assets/raven-logo.jpg'),
            title: 'RAVEN (Reconstruction, Analysis and Visualization of Metabolic Networks) Toolbox is a software suite that allows for semi-automated reconstruction of genome-scale models',
            description: 'RAVEN is primarily intended for the generation and curation of genome-scale models by using published models and/or the MetaCyc and KEGG databases, coupled with extensive gap-filling and quality control features. Furthermore, the software incorporates functionality to contextualize generic models using the task-based INIT algorithm, for generating e.g. tissue-specific models. RAVEN also contains methods for visualizing simulation results and omics data, as well as a range of methods for performing simulations and analyzing the results. The software is a useful tool for system-wide data analysis in a metabolic context and for streamlined reconstruction of metabolic networks based on protein homology and expression data.',
            citation: 'Wang, H., Marcišauskas, S., Sánchez, B.J., Domenzain, I., Hermansson, D., Agren, R., Nielsen, J., Kerkhoven, E.J. (2018) RAVEN 2.0: A versatile toolbox for metabolic network reconstruction and a case study on Streptomyces coelicolor. PLOS Computational Biology, 14, e1006541.',
            citation_url: 'https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006541&rev=2' },
          { name: 'BioMet-toolbox',
            link: 'http://biomet-toolbox.chalmers.se/',
            img: require('../assets/biomet-logo.png'),
            title: 'The BioMet Toolbox 2.0 integrates a number of functionalities enabling the user to work with biological data in a web interface',
            description: 'The distinguishing feature is to provide a web interface to tools for metabolic pathways and omics analysis developed under different platform-dependent environments enabling easy access to these computational tools.',
            citation: 'Manuel Garcia-Albornoz, Subazini Thankaswamy-Kosalai, Avlant Nilsson, Leif Väremo, Intawat Nookaew, Jens Nielsen. <i>BioMet Toolbox 2.0: genome-wide analysis of metabolism and omics data</i>. Nucleic Acids Research, Volume 42, Issue W1, 1 July 2014, Pages W175–W181',
            citation_url: 'https://academic.oup.com/nar/article/42/W1/W175/2436233' },
        ],
        Databases: [
          { name: 'YSeq Browser',
            link: 'http://www.sysbio.se/Yseq/',
            img: require('../assets/YseqLogo.png'),
            title: 'Genome and transcriptome (RNAseq and Microarray) browser of Saccharomyces cerevisiae',
            description: 'Yseq provides a useful and comprehensive comparison between the two platforms (RNA-seq and microrrays) for gene expression analysis and addresses the contribution of the different steps involved in the analysis of RNA-seq data',
            citation: 'Nookaew, I., Papini, M., Pornputtapong, N., Scalcinati, G., Fagerberg, L., Uhlén, M., & Nielsen, J. (2012). <i>A comprehensive comparison of RNA-Seq-based transcriptome analysis from reads to differential gene expression and cross-comparison with microarrays: a case study in Saccharomyces cerevisiae</i>. Nucleic acids research, 40(20), 10084-10097',
            citation_url: 'https://academic.oup.com/nar/article/40/20/10084/2414805' },
          { name: 'yApoptosis',
            link: 'http://www.ycelldeath.com/yapoptosis/',
            img: require('../assets/YAp_logo.gif'),
            title: 'yApoptosis is an extensively-curated database dedicated for researchers working on yeast apoptosis',
            description: 'It is an open platform established to facilitate the organization and sharing of knowledge.',
            citation: 'Wanichthanarak, K., Cvijovic, M., Molt, A., & Petranovic, D. <i>yApoptosis: yeast apoptosis database</i>. Database, 2013',
            citation_url: 'https://academic.oup.com/database/article/doi/10.1093/database/bat068/341971' },
          { name: 'yStreX',
            link: 'http://www.ystrexdb.com/',
            img: require('../assets/logo_ystrex.png'),
            title: 'yStreX is an online database that collects, stores and distributes genome-wide expression data generated in the studies of stress responses',
            description: 'Using Saccharomyces cerevisiae as the model organism, we constructed a web interface with interactive visualization to provide intuitive access and to display the queried data for users with no background in bioinformatics.',
            citation: 'Kwanjeera Wanichthanarak, Intawat Nookaew, Dina Petranovic. <i>yStreX: yeast stress expression database</i>. Database, Volume 2014, 1 January 2014',
            citation_url: 'https://academic.oup.com/database/article/doi/10.1093/database/bau068/2634682' },
          { name: 'HCSD',
            link: 'http://cancersecretome.org/',
            img: require('../assets/HCSD_logo.png'),
            title: 'The human cancer secretome database (HCSD) is a comprehensive database for human cancer secretome data',
            description: 'Query, and compare, publicly available proteomics data published in the field of cancer secretome and tumor microenviroment, and visualize the predicted secretory features and post-translational modification sites (PTMs) for each protein.',
            citation: 'Feizi, A., Banaei-Esfahani, A., Nielsen, J. (2015) <i>HCSD: the human cancer secretome database</i>. Database 2015',
            citation_url: 'https://academic.oup.com/database/article/doi/10.1093/database/bav051/2433184' },
        ],
        APIs: [
          { name: 'Metabolic Atlas API',
            link: 'api/',
            img: '/img/logo.png',
            title: 'Access Metabolic Atlas programatically',
            description: 'The API is a set of URL requests that will respond to the query parameters with JSON formatted text. Our implementation gives the possibility of trying out different queries to see what the results would look like.' },
          { name: 'Protein Atlas Programmatic data access',
            link: 'https://www.proteinatlas.org/about/help/dataaccess',
            img: require('../assets/hpa.png'),
            title: 'Access Protein Atlas programatically',
            description: 'Download a subset of the data provided in XML, RDF or TSV format, either as individual queries or search queries. ',
          },
        ],
      },
    };
  },
};

</script>
