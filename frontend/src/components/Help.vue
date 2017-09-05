<template>
  <div class="columns">
    <div class="container column is-8">
      <h2 class="title is-2">Network graph</h2>
      <br>

      <a name="search" />
      <h3 id="reportermetabolites" class="title is-3">Search</h3>

      <h4 class="title is-4">Search bar</h4>
      <p><b>Search</b> for either metabolite, enzyme, or reaction by any number of 'attributes'.</p>
      <p>Search for metabolite by identifier, name, or synonym, for example M_m01249c or uracil.</p>
      <p>Once you start typing it will pull out all possible matches from the database and show these in the drop-down.</p>
      <p>Depending on what type of 'hit' your requests results in (metabolite, enzyme, or reaction)
        a number of different green buttons are shown:
        <ul>
          <li>For a metabolite:
            <ul>
              <li><a href="">Closest interaction partners</a></li>
              <li><a href="">Metabolite</a></li>
            </ul>
          </li>
          <li>For an enzyme:
            <ul>
              <li><a href="">Closest interaction partners</a></li>
              <li><a href="">Enzyme</a></li>
            </ul>
          </li>
          <li>For a reaction:
            <ul>
              <li><a href="">Reaction</a></li>
            </ul>
          </li>
        By pressing one of these you go directly to that page...<br/>
        <b>alternatively</b> you can press Enter and be take to a table of
        all possible <a href="#searchresults">search results</a> that fit your term.
      </p>
      <br>

      <h4 class="title is-4">Search results</h4>
      <p>If you for instance searched for ATP and then pressed Enter you will see
        that there are 11 metabolites that match this search term because
        ATP is found in 8 compartments, and dATP in 3.<br/>
        In addition 11 enzymes match ATP, because there are whole families of
        ATP-related proteins.<br/>
        In addition 739 reactions use, or produce ATP.<br/>
        Click on the ID in order to be taken to that page.
      </p>
      <br/>

      <h3 id="reportermetabolites" class="title is-3">The whole metabolic network</h3>
      <p>Find and visualize metabolite networks in the context of reactions, pathways, compartments or for the whole model map</p>
      <br>

      <h3 id="closestpartners" class="title is-3">Closest interaction partners</h3>
      <p>We treat all chemical equations (eg reactions) form HMR2.0 as binary "interactions". This gives us the option of "zooming in" around a given ReactionComponent (species in SBML) (for example an enzyme from HPA).</p>
      <p>This could be used to "determine" how important a given ReactionComponent is, and how a set of ReactionComponents interact and how their expression levels change between tissues.</p>
      <br>

        <h4 class="title is-4">The cytoscape graph</h4>

          <h5 id="graphcustomisations" class="title is-5">Graph customization</h5>

          <h6 id="shapecolor">Shape and color</h6>
          <p>It is possible to change shape and color for the proteins and the metabolites shown in the graph.
            This is done by pressing the <b>Options</b> button.<br/>
            Here you are presented with a number of options for what to do with your Enzymes and Metabolite.<br/>
            If you want to show Expression levels see the
            <a href="#expression levels">expression levels</a> section below.
          </p>
          <h6 id="zoominout">Zoom in and out</h6>
          <p>Simply press either the <b>+</b> or <b>-</b> button to zoom in the graph.</p>
          <h6>Fit the graph to the window size</h6>
          <p>Press the <b>Fit</b> button will zoom in, or out depending, to fit
            all the edges and nodes of the graph to the window size.</p>
          <br/>

          <h6 id="expressionlevels" class="title is-5">Expression levels</h6>
          <p>To show expression levels:<br/>
            First click the <b>Options</b> button, then click in the "Show expression levels" tick box.
            This will at the moment, go to HPA and pull in the expression levels for all
            the proteins in the current graph, and then the drop-down box will be enabled,
            and here all the HPA tissue RNA-seq data is then available.
            The moment you select one tissue it will color the proteins according to that.
          </p>
          <br/>

          <h6 class="title is-5">Export graph</h6>
          <p>Click the <b>Export graph</b> button, and you will be presented with
            two options: Graphml or PNG.<br/>
            The first is a Cytoscape compatible graphml format, including a
            stylesheet in order to make it identical to the current view.
          </p>
          <br />

        <h4 id="propertybox" class="title is-5">The property of the selected metabolite/enzyme box</h4>
        <p>Depending on whether you have selected (by clicking on the graph) a
          metabolite or an enzyme different fields will be shown here.
          But generally this should display the most relevant information for
          the selected reaction component, such as function, activity, and mass.
        </p>
        <br />

        <h4 id="reactioncomponenttable" class="title is-4">Reaction component table</h4>
        <p>All the reaction components, eg the nodes, of the above graph are shown in
          this table, along with some basic information such as name and type. <br/>
          Selecting a row will select it in the graph, and vice verse.
        </p>
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

      <h2 id="models" class="title is-2">Models</h2>
      <p>List all models that the group have made</p>
      <br>

      <h2 id="resources" class="title is-2">Resources</h2>
      <br>

      <h3 id="tools" class="title is-3">Tools</h3>
      <p>List the tools...</p>
      <br>

      <h3 id="api" class="title is-3">API</h3>
      <p>The API allows to retrieve...</p>
      <br>

    </div>
    <div id="help-sidebar"class="column is-3">
      <div class="box">
        GEM visualisation<br/>
        &nbsp;&nbsp;<a href="#search">Search</a><br/>
        &nbsp;&nbsp;<a href="#searchresults">Search results</a><br/>
        &nbsp;&nbsp;<a href="#reportermetabolites">The whole metabolic network</a><br/>
        &nbsp;&nbsp;<a href="#closestpartners">Closest interaction partners</a><br/>
        &nbsp;&nbsp;&nbsp;&nbsp;<a href="#graphcustomisations">Graph customisations</a><br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="#shapecolor">Shape and color</a><br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="#graphcustomisations">Zoom in/out</a><br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="#zoominout">Fit</a><br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="#expressionlevels">Color by expression levels</a><br/>
        &nbsp;&nbsp;&nbsp;&nbsp;<a href="#propertybox">Property box</a><br/>
        &nbsp;&nbsp;&nbsp;&nbsp;<a href="#reactioncomponenttable">Reaction component table</a><br/>
        <a href="#models">Models</a><br/>
        <a href="#resources">Resources</a><br/>
        &nbsp;&nbsp;<a href="#tools">Tools</a><br/>
        &nbsp;&nbsp;<a href="#tools">Databases</a><br/>
        &nbsp;&nbsp;<a href="#api">API</a><br/>
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
