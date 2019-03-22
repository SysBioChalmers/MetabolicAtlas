<template>
  <section class="section extended-section">
    <div class="container is-size-5">
      <div class="columns is-variable is-8">
        <div class="column is-half has-text-justified">
          <p>
            The Divion of Systems and Synthetic Biology is lead by <a href="https://www.sysbio.se/labs/nielsen/" target="_new">Professor Jens Nielsen</a>, and is part of the Department of Biology and Biological Engineering at the <a href="https://www.chalmers.se" target="_new">Chalmers University of Technology</a>.<br>
            The research focus of the content of this website is <b>metabolism in a systems biology context</b>. The goal is to collect many curated Genome-Scale Metabolic Models (GEMs), and to bring these models closer to <a href="https://en.wikipedia.org/wiki/FAIR_data" target="_new">FAIR principles</a>. To this end, the website also provides visualisations and comparisons of the GEMs, and links to <a href="resources">resources</a>: algorithms, other databases, and more general software applications (like RAVEN and PIANO).<br>
            In short, the vision is to create a one-stop-shop for everything metabolism related, starting with <a href="https://www.sysbio.se/labs/nielsen/#publications">the publications of the Nielsen lab</a>.
          </p>
        </div>
        <div class="column is-half has-text-justified">
          <img width="100%" src="../assets/group_18a.jpg">
          <center>The SysBio group 2018</center>
        </div>
      </div>
      <div class="columns is-variable is-8">
        <div class="column is-half has-text-justified">
          <h3 class="subtitle is-4">The Metabolic Atlas</h3>
          <p>The Metabolic Atlas is a freely available electronic database containing detailed information about a set of GEMs, especially Human1 and Yeast8. These are two "reference" models containing all possible reactions that could occur in human, and yeast, respectively.</p><br>
          <p>We aim to facilitate the understanding of a model by showing how reactions are connected into subsystems, with the ability to zoom in on a particular pathway.</p>
          <p>Metabolic Atlas is intended to be used for applications in metabolomics, clinical chemistry, biomarker discovery and general education.</p><br>
          For versions and release notes, <a href="https://github.com/SysBioChalmers/MetabolicAtlas/releases" target="_blank">check the GitHub page</a>.
        </div>
        <div class="column is-half has-text-justified">
          <div class="box">
            <h4 class="subtitle is-size-4 has-text-primary has-text-centered">Citing the Metabolic Atlas</h4>
            <p>Paper under consideration</p>
            <!-- <p>
              <a href="" target="_blank">APA style reference with DOI</a><br><br>
              Abstract here
              <br><br>
              Genome scale metabolic model in the publication <a @click="viewGem()">Human1</a>
            </p> -->
          </div>
        </div>
      </div>
      <div class="columns is-variable is-8">
        <div class="column has-text-justified">
          <h2 class="subtitle is-4">External resources</h2>
          <p>Metabolic Atlas would not be possible without the following excellent sources of information:</p>
          <ul>
            <li><h4><a href="http://proteinatlas.org" target="_blank">The Human Protein Atlas</a></h4></li>
            <li><h4><a href="http://www.genome.jp/kegg/" target="_blank">KEGG: Kyoto Encyclopedia of Genes and Genomes</a></h4></li>
            <li><h4><a href="http://www.uniprot.org" target="_blank">UniProt</a></h4></li>
            <li><h4><a href="http://www.hmdb.ca/" target="_blank">The Human Metabolome Database</a></h4></li>
          </ul><br>
          <h2 class="subtitle is-size-3">Contact</h2>
            <p>
              For any questions, comments or suggestions please contact <a href="mailto:">contact[at]metabolicatlas.org</a>
            </p>
            <h5><a href="https://www.sysbio.se/contact/" target="blank"> Division of Systems and Synthetic Biology</a></h5>
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
      this.$router.push({ name: 'gems' });
      EventBus.$emit('viewGem', 'Human1');
    },
  },
};
</script>

<style lang="scss"></style>
