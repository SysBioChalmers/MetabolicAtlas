<template>
  <section class="section extended-section" id="about">
    <div class="container">
      <div class="columns">
        <div class="column is-half text">
          <p>
            The Divion of Systems and Synthetic Biology is lead by
            <a href="http://sysbio.se/Lab_Nielsen/lab_nielsen.html" target="_new">Professor Jens Nielsen</a>,
            and is part of the Department of Biology and Biological Engineering at the
            <a href="http://www.chalmers.se" target="_new">Chalmers University of Technology</a>.
            <br><br>
            The research focus of the content of this site,
            is on <b>systems biology of metabolism</b> and the goal is to
            collect all our curated Genome-Scale Metabolic
            <a href="models">Models</a>,
            <a href="http://www.metabolicatlas.org">visualisations</a> of the same,
            <a href="resources">resources</a>
            (like the possibility to compare models), algorithms (like the reporter metabolites),
            other types of <a href="resources#databases">databases</a>
            (like HSCD), and more general <a href="resources#tools">software applications</a>
            (like RAVEN and PIANO) here. In short, this should be your one-stop-shop for
            everything metabolism related that we have
            <a href="http://www.sysbio.se/Lab_Nielsen/publications.html">published</a>.
          </p><br>
          <h2 class="subtitle is-3">The Metabolic Atlas</h2>
          <p>The Metabolic Atlas is a freely available electronic database containing
            detailed information about a set of GEMs, especially the HMR2.0 and the
            yeast 8.0. These are two "reference" models containing all possible
            reactions that could occur in human, and yeast, respectively.
          </p>
          <p>With special focus on how reactions are connected into sub-systems
            and trying to link in external relevant information so that it should
            become easier to understand what your current model is capable or, and
            especially if you "zoom in" on a particular pathway, what would be the
            biological interpretation of this?
          </p>
          <p>It is intended to be used for applications in metabolomics, clinical chemistry,
            biomarker discovery and general education.
          </p><br>
        </div>
        <div class="column is-half text">
          <img width="100%" src="http://sysbio.se/pics/group/group18A_620.jpg">
          <center><br>The group</center>
        </div>
      </div>
      <div class="columns">
        <div class="column text">
          <h4 id="releaseNotes" class="subtitle is-3">Release notes</h4>
          <p>
            <b>Version 1.0</b> - a complete overhaul 2018-10-01; A completely new
            version of the site was launched, complete with manually drawn map of HMR2.0.
          </p><br>
          <h2 class="subtitle is-3">External resources</h2>
          <p>Metabolic Atlas would not be possible without the following excellent sources of information:</p>
          <ul>
            <li><h5><a href="http://proteinatlas.org" target="_blank">The Human Protein Atlas</a></h5></li>
            <li><h5><a href="http://www.genome.jp/kegg/" target="_blank">KEGG: Kyoto Encyclopedia of Genes and Genomes</a></h5></li>
            <li><h5><a href="http://www.uniprot.org" target="_blank">UniProt</a></h5></li>
            <li><h5><a href="http://www.hmdb.ca/" target="_blank">The Human Metabolome Database</a></h5></li>
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
          </p>
          <h2 class="title is-2">Contact</h2>
          <p>
            For any questions, comments or suggestions please contact <a href="mailto:">contact@metabolicatlas.org</a>.
          </p>
          <br>
          <div class="columns">
            <div class="column is-half">
              <h5><a href="http://sysbio.se" target="blank"> Divion of Systems and Synthetic Biology</a></h5><br>
              <p>For any questions, comments or suggestions please contact
                <a href="mailto:">contact@metabolicatlas.org</a>.
              </p><br>
              <p>
                Chalmers University of Technology<br>
                Department of Biology and Biological Engineering<br>
                Kemigården 4, Forskarhus I (Research building I), 6th floor<br>
                SE-412 96 Göteborg Sweden<br>
              </p><br>
              <p>
                Postal and delivery address<br>
                Chalmers University of Technology<br>
                Department of Biology and Biological Engineering<br>
                Division of Systems and Synthetic Biology<br>
                Kemivägen 10<br>
                SE-412 96 Göteborg<br>
                Sweden<br>
                Please include reference to a person at Systems and Synthetic Biology.<br>
              </p>
            </div>
            <div class="column is-half">
              <img src="http://www.sysbio.se/pics/KEMI.jpg" />
            </div>
          </div>
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

<style lang="scss">
#about {
  .text {
    text-align: justify;
  }
}

</style>
