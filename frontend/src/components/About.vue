<template>
  <div>
    <div class="container">
      <h2 class="title is-2">About us</h2>
      <p class="box">
         tell more about the group
      </p>
      <br>
      <h2 class="title is-2">The metabolic Atlas project</h2>
      <div class="text">
        <h4 class="subtitle is-4">Motivation</h4>
        <p class="text">
          nice motivation text here
        </p>
      </div>
      <br>
      <div class="text">
        <h4 class="subtitle is-4">Objectives</h4>
        <p class="text">
          nice objectif text here
        </p>
      </div>
      <br>
      <div class="text">
        <h4 class="subtitle is-4">Background and history</h4>
        <p class="text">
          nice history here
        </p>
      </div>
      <br>
      <div class="text">
        <h4 class="subtitle is-4">Release notes</h4>
        <p class="text">
          what changed - what's new
        </p>
      </div>
      <br>
      <h2 class="title is-2">External resources</h2>
      <div class="text">
        <p>Metabolic Atlas would not be possible without the following excellent sources of open data.</p>
        <br>
        <ul>
          <li><h5 class="title is-5"><a href="http://proteinatlas.org" target="_blank">The Human Protein Atlas</h5></li>
          <li><h5 class="title is-5"><a href="http://www.genome.jp/kegg/" target="_blank">KEGG: Kyoto Encyclopedia of Genes and Genomes</h5></li>
          <li><h5 class="title is-5"><a href="http://www.uniprot.org" target="_blank">UniProt</h5></li>
          <li><h5 class="title is-5"><a href="http://www.hmdb.ca/" target="_blank">The Human Metabolome Database</h5></li>
        </ul>
      </div>
      <br>
      <h2 class="subtitle is-2">Citing Metabolic Atlas</h2>
      <p class="text">
        Please use the following paper for citation: <a href="http://database.oxfordjournals.org/content/2015/bav068.full">Human metabolic atlas: an online resource for human metabolism</a>
        <br><br>
        <strong>Natapol Pornputtapong, Intawat Nookaew and Jens Nielsen</strong>
        <br>
        Human tissue-specific genome-scale metabolic models (GEMs) provide comprehensive understanding of human metabolism, which is of great value to the biomedical research community. To make this kind of data easily accessible to the public, we have designed and deployed the human metabolic atlas (HMA) website (http://www.metabolicatlas.org). This online resource provides comprehensive information about human metabolism, including the results of metabolic network analyses. We hope that it can also serve as an information exchange interface for human metabolism knowledge within the research community. The HMA consists of three major components: Repository, Hreed (Human REaction Entities Database) and Atlas. Repository is a collection of GEMs for specific human cell types and human-related microorganisms in SBML (System Biology Markup Language) format. The current release consists of several types of GEMs: a generic human GEM, 82 GEMs for normal cell types, 16 GEMs for different cancer cell types, 2 curated GEMs and 5 GEMs for human gut bacteria. Hreed contains detailed information about biochemical reactions. A web interface for Hreed facilitates an access to the Hreed reaction data, which can be easily retrieved by using specific keywords or names of related genes, proteins, compounds and cross-references. Atlas web interface can be used for visualization of the GEMs collection overlaid on KEGG metabolic pathway maps with a zoom/pan user interface. The HMA is a unique tool for studying human metabolism, ranging in scope from an individual cell, to a specific organ, to the overall human body. This resource is freely available under a Creative Commons Attribution-NonCommercial 4.0 International License.
      </p>
    </div>
  </div>
</template>

<script>

export default {
  name: 'about',
};
</script>

<style lang="scss">

.text {
  padding-left: 0.75em;
}

</style>
