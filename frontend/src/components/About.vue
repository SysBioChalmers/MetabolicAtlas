<template>
  <section class="section extended-section">
    <div class="container is-size-5">
      <div class="columns">
        <div class="column is-half has-text-justified">
          <p>
            The Divion of Systems and Synthetic Biology is lead by <a href="https://www.sysbio.se/labs/nielsen/" target="_new">Professor Jens Nielsen</a>, and is part of the Department of Biology and Biological Engineering at the <a href="https://www.chalmers.se" target="_new">Chalmers University of Technology</a>.<br><br>
            The research focus of the content of this website is <b>metabolism in a systems biology context</b>. The goal is to collect many curated Genome-Scale Metabolic Models (GEMs), and to bring these models closer to <a href="https://en.wikipedia.org/wiki/FAIR_data" target="_new">FAIR principles</a>. To this end, the website also provides visualisations and comparisons of the GEMs, <a href="resources">resources</a>: algorithms (like the reporter metabolites), other databases (like HSCD), and more general software applications (like RAVEN and PIANO).<br><br>
            In short, the vision is to create a one-stop-shop for everything metabolism related, starting with <a href="https://www.sysbio.se/labs/nielsen/#publications">the publications of the Nielsen lab</a>.
          </p><br><br>
          <h3 class="subtitle is-3">The Metabolic Atlas</h3>
          <p>The Metabolic Atlas is a freely available electronic database containing detailed information about a set of GEMs, especially Human1 and Yeast8. These are two "reference" models containing all possible reactions that could occur in human, and yeast, respectively.</p>
          <p>We aim to facilitate the understanding of a model by showing how reactions are connected into subsystems, with the ability to "zoom in" on a particular pathway.</p>
          <p>Metabolic Atlas is intended to be used for applications in metabolomics, clinical chemistry, biomarker discovery and general education.</p><br>
        </div>
        <div class="column is-half has-text-justified">
          <img width="100%" src="http://sysbio.se/pics/group/group18A_620.jpg">
          <center><br>The group</center>
        </div>
      </div>
      <div class="columns">
        <div class="column has-text-justified">
          <h4 class="subtitle is-3">Release notes</h4>
          <p>
            <b>Version 1.0</b> - a complete overhaul 2018-10-01; A completely new
            version of the site was launched, complete with manually drawn map of HMR2.0.
          </p><br>
          <h2 class="subtitle is-3">External resources</h2>
          <p>Metabolic Atlas would not be possible without the following excellent sources of information:</p>
          <ul>
            <li><h4><a href="http://proteinatlas.org" target="_blank">The Human Protein Atlas</a></h4></li>
            <li><h4><a href="http://www.genome.jp/kegg/" target="_blank">KEGG: Kyoto Encyclopedia of Genes and Genomes</a></h4></li>
            <li><h4><a href="http://www.uniprot.org" target="_blank">UniProt</a></h4></li>
            <li><h4><a href="http://www.hmdb.ca/" target="_blank">The Human Metabolome Database</a></h4></li>
          </ul><br>
          <h2 class="subtitle is-3">Citing the Metabolic Atlas</h2>
          <p>
            Please use the following paper for citation: <a href="http://database.oxfordjournals.org/content/2015/bav068.full" target="_blank">Human metabolic atlas: an online resource for human metabolism</a>
            <br><br>
            <strong>Natapol Pornputtapong, Intawat Nookaew and Jens Nielsen</strong>
            <br>
            Human tissue-specific genome-scale metabolic models (GEMs) provide comprehensive understanding of human metabolism, which is of great value to the biomedical research community. To make this kind of data easily accessible to the public, we have designed and deployed the human metabolic atlas (HMA) website (http://www.metabolicatlas.org). This online resource provides comprehensive information about human metabolism, including the results of metabolic network analyses. We hope that it can also serve as an information exchange interface for human metabolism knowledge within the research community. The HMA consists of three major components: Repository, Hreed (Human REaction Entities Database) and Atlas. Repository is a collection of GEMs for specific human cell types and human-related microorganisms in SBML (System Biology Markup Language) format. The current release consists of several types of GEMs: a generic human GEM, 82 GEMs for normal cell types, 16 GEMs for different cancer cell types, 2 curated GEMs and 5 GEMs for human gut bacteria. Hreed contains detailed information about biochemical reactions. A web interface for Hreed facilitates an access to the Hreed reaction data, which can be easily retrieved by using specific keywords or names of related genes, proteins, compounds and cross-references. Atlas web interface can be used for visualization of the GEMs collection overlaid on KEGG metabolic pathway maps with a zoom/pan user interface. The HMA is a unique tool for studying human metabolism, ranging in scope from an individual cell, to a specific organ, to the overall human body. This resource is freely available under a Creative Commons Attribution-NonCommercial 4.0 International License.
            <br><br>
            Related GEM <a @click="viewGem()">Human Metabolic Reaction v2.00</a>
          </p><br><br>
          <h2 class="title is-2">Contact</h2>
            <h5><a href="https://www.sysbio.se/contact/" target="blank"> Division of Systems and Synthetic Biology</a></h5><br>
            <p>
              For any questions, comments or suggestions please contact <a href="mailto:">contact@metabolicatlas.org</a>.
            </p>
        </div>
      </div>
      </div>
    </div>
  </section>
</template>

<script>

import { default as EventBus } from '../event-bus';

export default {
  name: 'about',
  methods: {
    viewGem() {
      EventBus.$emit('viewGem', 'HMR2');
      this.$router.push({ name: 'gems' });
    },
  },
};
</script>

<style lang="scss"></style>
