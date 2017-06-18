<template>
  <div class="about">
    <h1 class="title is-1">About</h1>
    <br>
    <div class="container">
      <h2 class="title is-2">Network graph</h2>
      <h3 id="closestpartners" class="title is-3">Closest interaction partners</h3>
      <p>We treat all chemical equations (eg reactions) form HMR2.0 as binary "interactions". This gives us the option of "zooming in" around a given ReactionComponent (species in SBML) (for example an enzyme from HPA).</p>
      <p>This could be used to "determine" how important a given ReactionComponent is, and how a set of ReactionComponents interact and how their expression levels change between tissues.</p>
      <br>
      <h3 id="connectedmetabolites" class="title is-3">Catalysed reactions</h3>
      <p>Take an enzyme, in the form of an Ensembl Gene Identifier (for example ENSG00000164303 or ENSG00000180011) then it will find all reactions that this enzyme modifies, and for each of these reactions pull out the reactants (shape=heptagon) and the products (shape=octagon), i.e. the metabolites)</p>
      <br>
      <br>
      <h2 class="title is-2">External resources</h2>
      <p>Metabolic Atlas would not be possible without the following excellent sources of open data.</p>
      <br>
      <ul>
        <li><h5 class="title is-5"><a href="http://proteinatlas.org" target="_blank">The Human Protein Atlas</h5></li>
        <li><h5 class="title is-5"><a href="http://www.genome.jp/kegg/" target="_blank">KEGG: Kyoto Encyclopedia of Genes and Genomes</h5></li>
        <li><h5 class="title is-5"><a href="http://www.uniprot.org" target="_blank">UniProt</h5></li>
        <li><h5 class="title is-5"><a href="http://www.uniprot.org" target="_blank">The Human Metabolome Database</h5></li>
      </ul>
    </div>
  </div>
</template>

<script>

export default {
  name: 'about',
};
</script>

<style lang="scss">
</style>
