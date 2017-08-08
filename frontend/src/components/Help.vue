<template>
  <div class="columns">
    <div class="container column is-8">
      <h2 class="title is-2">Network graph</h2>
      <br>

      <h3 id="reportermetabolites" class="title is-3">Search</h3>
      <p></p>
      <br>

        <h4 class="title is-4">Search bar</h4>
        <br>

        <h4 class="title is-4">Search page</h4>
        <br>

      <h3 id="reportermetabolites" class="title is-3">Repoter metabolites</h3>
      <p>Find and visualize metabolite networks in the context of reactions, pathways, compartements or for the whole model map</p>
      <br>

      <h3 id="closestpartners" class="title is-3">Closest interaction partners</h3>
      <p>We treat all chemical equations (eg reactions) form HMR2.0 as binary "interactions". This gives us the option of "zooming in" around a given ReactionComponent (species in SBML) (for example an enzyme from HPA).</p>
      <p>This could be used to "determine" how important a given ReactionComponent is, and how a set of ReactionComponents interact and how their expression levels change between tissues.</p>
      <br>

        <h4 class="title is-4">Network graph</h4>
        <br>

          <h5 class="title is-5">Graph customization</h5>
          <br>

          <h5 class="title is-5">Export graph</h5>
          <br>

          <h5 class="title is-5">Side bar information</h5>
          <br>

          <h5 class="title is-5">Expression levels</h5>
          <br>

        <h4 class="title is-4">Metabolic component table</h4>
        <br>

          <h5 class="title is-5">Export</h5>
          <br>


      <h3 id="connectedmetabolites" class="title is-3">Catalysed reactions</h3>
      <p>Take an enzyme, in the form of an Ensembl Gene Identifier (for example ENSG00000164303 or ENSG00000180011) then it will find all reactions that this enzyme modifies, and for each of these reactions pull out the reactants (shape=heptagon) and the products (shape=octagon), i.e. the metabolites)</p>
      <br>

        <h4 class="title is-4">Network graph</h4>
        <br>

          <h5 class="title is-5">Side bar information</h5>
          <br>

        <h4 class="title is-4">Reaction component table</h4>
        <br>

          <h5 class="title is-5">Export</h5>
          <br>

      <h3 id="metabolites" class="title is-3">Metabolites</h3>
      <p>Show the description of the current selected metabolite</p>
      <br>

        <h4 class="title is-4">Reactome table</h4>
        <br>

      <h2 class="title is-2">Models</h2>
      <br>

      <h2 class="title is-2">Resources</h2>
      <br>

      <h3 id="api" class="title is-3">Tools</h3>
      <p>List the tools...</p>
      <br>

      <h3 id="api" class="title is-3">API</h3>
      <p>The API allows to retrieve...</p>
      <br>

    </div>
    <div id="help-sidebar"class="column is-3">
      <div class="box">
        help content
      <div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'help',
};
</script>

<style lang="scss">
</style>
