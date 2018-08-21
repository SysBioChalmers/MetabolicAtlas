<template>
  <section class="section extended-section">
    <div class="container">
      <div class="columns help-div">
        <div class="container column is-10">
          <h2 class="title is-2">GEM visualisation</h2>
          <hr>
          <h3 id="search" class="title is-3">Search</h3>

          <h4 class="title is-4">Search bar</h4>
          <b>Searches</b> for the term in metabolites, enzymes, subsystems, reactions, and reaction_components. </br>
            &nbsp;<u>Metabolites</u>: kegg_id, hmdb_id, hmdb_name contains </br>
            &nbsp;<u>Enzymes</u>: (uniprot_acc) </br>
            &nbsp;<u>Subsystems</u>: (name contains) </br>
            &nbsp;<u>Reactions</u>: (equation contains) </br>
            &nbsp;<u>ReactionComponent</u>: (id, short name contains, long name contains, formula contains) </br>
          Once you start typing it will pull out all possible matches from the database,
          <i>for this given model (!)</i>, and show these in the drop-down.
          Depending on what type of 'hit' your requests results in (metabolite, enzyme, or reaction)
            a number of different green buttons are shown:
            <ul>
              <li>For a metabolite:
                <ul>
                  <li><a href="#closestpartners">Closest interaction partners</a></li>
                  <li><a href="#metabolitepage">Metabolite</a> page</li>
                </ul>
              </li>
              <li>For an enzyme:
                <ul>
                  <li><a href="#closestpartners">Closest interaction partners</a></li>
                  <li><a href="#enzymepage">Enzyme</a> page</li>
                </ul>
              </li>
              <li>For a reaction:
                <ul>
                  <li><a href="#reactionpage">Reaction</a> page</li>
                </ul>
              </li>
            </ul>
            By pressing one of these you go directly to that page...<br>
            <i>alternatively</i> you can press Enter and be take to a table of
            all possible <a href="#searchresults">search results</a> that fit your term.
          </p>
          <br>

          <h4 class="title is-4">Search results</h4>
          <p>If you for instance searched for ATP and then pressed Enter you will see
            that there are 11 metabolites that match this search term because
            ATP is found in 8 compartments, and dATP in 3.<br>
            In addition 11 enzymes match ATP, because there are whole families of
            ATP-related proteins.<br>
            In addition 739 reactions use, or produce ATP.<br>
            Click on the ID in order to be taken to the corresponding page.
          </p>
          <p>
            On this page you also have the option of searching, but here it will
            instead search in the entire data, eg <i>across GEMs</i>.
          </p>

          <hr>

          <h3 id="wholenetwork" class="title is-3">The whole metabolic network</h3>
          <p>Find, and visualize, reactions, metabolites, enzymes, in the context of
            compartment and pathways, on the background of the for the whole map
            for the chosen GEM </p>
          <br>

          <h3 id="closestpartners" class="title is-3">Closest interaction partners</h3>
          <p>
            We treat all chemical equations (eg reactions) form HMR2.0 as binary "interactions".
            This gives us the option of "zooming in" around a given ReactionComponent
            (species in SBML) (for example an enzyme from HPA). <br>
            Take for example the reaction R_HRM_3905
            <i>ethanol[c] + NAD+[c] => acetaldehyde[c] + H+[c] + NADH[c]</i>,
            modified by 9 ADH proteins, this would give a 'neighbourhood' of
            ethanol, NAD+, acetaldehyde, H+, NADH, ADH1B, ADH1C, ADH1A, ADHFE1,
            ADH7, ADH6, ADH4, ZADH2, and ADH5.<br>
            But these metabolites also participates in other reactions, so you
            would include that information as well.
          </p>
          <p>
            This could be used to "determine" how important a given ReactionComponent is,
            and how a set of ReactionComponents interact and how their expression
            levels change between tissues.
          </p>
          <br>

            <h4 id="closest_graph" class="title is-4">The cytoscape graph</h4>

              <h5 id="graphcustomisations" class="title is-5">Graph customization</h5>

              <h6 id="shapecolor">Shape and color</h6>
              <p>
                It is possible to change shape and color for the proteins and the metabolites shown in the graph.
                This is done by pressing the <b>Options</b> button.<br>
                Here you are presented with a number of options for what to do with your Enzymes and Metabolite.<br>
                If you want to show Expression levels see the
                <a href="#expressionlevels">expression levels</a> section below.
              </p><br>
              <h6 id="zoominout">Zoom in and out</h6>
              <p>
                Simply press either the <b>+</b> or <b>-</b> button to zoom in the graph.
              </p><br>
              <h6 id="fitgraph">Fit the graph to the window size</h6>
              <p>Press the <b>Fit</b> button will zoom in, or out depending, to fit
                all the edges and nodes of the graph to the window size.
              </p>
              <br>
              <h6 id="expressionlevels" class="title is-6">Expression levels</h6>
              <p>To show expression levels:<br>
                First click the <b>Options</b> button, then click in the "Show expression levels" tick box.
                This will at the moment, go to HPA and pull in the expression levels for all
                the proteins in the current graph, and then the drop-down box will be enabled,
                and here all the HPA tissue RNA-seq data is then available.
                The moment you select one tissue it will color the proteins according to that.
              </p>
              <br>
              <div id="graphLegend" v-html="getExpLvlLegend()"></div>
              <br><br>

            <h5 id="export" class="title is-5">Export graph</h5>
            <p>Click the <b>Export graph</b> button, and you will be presented with
              two options: Graphml or PNG.<br>
              The first is a Cytoscape compatible graphml format, including a
              stylesheet in order to make it identical to the current view.
            </p>
            <br>
            <h4 id="propertybox_closest" class="title is-4">The property of the selected metabolite/enzyme box</h4>
            <p>Depending on whether you have selected (by clicking on the graph) a
              metabolite or an enzyme different fields will be shown here.
              But generally this should display the most relevant information for
              the selected reaction component, such as function, activity, and mass.
            </p>
            <br>
            <h4 id="reactioncomponenttable" class="title is-4">Metabolite list</h4>
            <p>All the metabolites, eg the nodes, of the above graph are shown in
              this table, along with some basic information such as name and type. <br>
              Selecting a row will select it in the graph, and vice verse.
            </p>
            <br>

          <hr>

          <h3 id="enzymepage" class="title is-3">Enzyme page</h3>
          <p>
            Take an enzyme, in the form of an Ensembl Gene Identifier
            (for example ENSG00000164303 or ENSG00000180011) then it will find all reactions
            that this enzyme modifies, and for each of these reactions pull out the reactants
            (shape=heptagon) and the products (shape=octagon), i.e. the metabolites)
          </p>
          <br>
            <h4 id="reaction_graph" class="title is-4">Reaction graph</h4>
            <p>
              The graph shows all the reactions that this protein is modifying as
              large green boxes. On <u>top</u> of each box the name of the reaction,
              for example R_HMR_7688, and the subsystem that it participates in,
              for example Tyrosine metabolism, is shown.
            </p>
            <p>
              Inside the green box <i>products</i> are circled by a <i>red</i> border,
              whereas the <i>consumed</i> metabolites are circled by a <i>blue</i> border.
            </p>
            <br>
            <h4 id="propertybox_enzyme" class="title is-4">The property of the selected metabolite/enzyme box</h4>
            <p>
              See the text for the closest interaction partners
              <a href="#propertybox_closest">property of selected</a>.
            </p>
            <br>
            <h4 id="metabolitelist" class="title is-4">Reaction component table</h4>
            <p>
              Lists all the reaction components, eg metabolites, that occurs in
              these reactions. <i>Please note</i> that this means that the same
              metabolite can, and often will, participate multiple times in this
              table as it, for example, will be produced by one reaction and then
              consumed by another.
            </p>

          <hr>

          <h3 id="metabolitepage" class="title is-3">Metabolite page</h3>
          <p>
            Show the description of the current selected metabolite.<br>
            This is a combination of annotations from the model, in-house
            annotations, and relevant information from external sources
            (eg HMDB for human data).
          </p>
          <br>
            <h4 id="reactometable" class="title is-4">Reactome table</h4>
            <p>
              Here all the reactions that the current metabolite participates in,
              either as a reactant or a product, are listed. <br>
              Please note that a metabolite is identified by the compartment in
              which it is found in (the last letter of the id), therefore
              you will only see reactions that occur in the current compartment,
              <u>unless</u> you press the <i>Expand to all compartments</i> button.<br>
              <i>Please note</i> that the number of reactions will be limited to
              200, no matter what.
            </p>

          <hr>

          <h3 id="reactionpage" class="title is-3">Reaction page</h3>
          <p>
            Show the description of the current selected reaction. <br>
            For example list the articles that is associated to the reaction.
          </p>

          <hr>

          <h2 id="models" class="title is-2">Models</h2>
          <p>
            List all models that the group have made, note that this include
            both older models that might no longer be maintained (for example HMR
            have been replaced with HMR2), but also those just published.
          </p>

          <hr>

          <h2 id="resources" class="title is-2">Resources</h2>
            <h5 id="tools" class="title is-4">Tools and Software</h5>
            <p>
              Some of the most relevant software tools and algorithms that the group
              have published could be found here, for example STIG-met, Kiwi, and Raven.
            </p>
            <br>
            <h5 id="databases" class="title is-4">Databases</h5>
            <p>
              Some of the databases that the group have generated are linked from here,
              for example human cancer secretome database (HCSD)
              and stress response in yeast (yStreX).
            </p>
            <br>
            <h5 id="api" class="title is-4">API</h5>
            <p>
              Link to the API for the GEM visualisation database part of this website,
              as hosted by Swagger.
            </p>
            <br>
            <h5 id="hreed_atlas" class="title is-4">Hreed and Atlas</h5>
            <p>
              List of all the legacy tools that were available on the old metabolicatlas.org
              site, such as Hreed and Atlas.
            </p>
          <br>

          <hr>

          <h2 id="gem_data" class="title is-2">GEM data</h2>
          <p>
            For information about the genome-scale metabolic models that are loaded
            into the database, please refer to the <a href="/About">About</a> page.
          </p>

          <hr>

        </div>
        <div class="column is-2"></div>
        <div id="help-sidebar"class="column is-2">
          <div class="box">
            <p class="menu-label">
              Table of Content
            </p>
            <ul class="menu-list">
              <li><a href="#GEMvis">GEM visualisation</a>
              <ul>
                <li>
                  <a href="#search">Search</a>
                  <ul class="menu-list">
                    <li><a href="#searchresults">Search results</a></li>
                  </ul>
                </li>
                <li><a href="#SVGs">The whole metabolic network</a></li>
                <li>
                  <a href="#closestpartners">Closest interaction partners</a>
                    <ul class="menu-list">
                      <li><a href="#closest_graph">Network graph</a>
                        <ul class="menu-list">
                          <li><a href="#graphcustomisations">Graph customisations</a>
                            <ul class="menu-list">
                              <li><a href="#shapecolor">Shape and color</a></li>
                              <li><a href="#zoominout">Zoom in/out</a></li>
                              <li><a href="#fitgraph">Fit the graph</a></li>
                              <li><a href="#expressionlevels">Expression levels</a></li>
                            </ul>
                          </li>
                          <li><a href="#export">Export Graph</a></li>
                        </ul>
                      </li>
                      <li><a href="#propertybox_closest">Property box</a></li>
                      <li><a href="#reactioncomponenttable">Reaction components</a></li>
                    </ul>
                  </li>
                  <li><a href="#enzymepage">Enzyme page</a></li>
                    <ul class="menu-list">
                      <li><a href="#reaction_graph">Reaction graph</a></li>
                      <li><a href="#propertybox_enzyme">Property box</a></li>
                      <li><a href="#metabolitelist">Metabolite list</a></li>
                    </ul>
                  <li><a href="#metabolitepage">Metabolite page</a>
                    <ul class="menu-list">
                      <li><a href="#reactometable">Reactome</a></li>
                    </ul>
                  </li>
                  <li><a href="#reactionpage">Reaction page</a></li>
                </ul>
              </li>
              <li><a href="#models">Models</a></li>
              <li>
                <a href="#resources">Resources</a>
                <ul class="menu-list">
                  <li><a href="#tools">Tools</a></li>
                  <li><a href="#databases">Databases</a></li>
                  <li><a href="#api">API</a></li>
                  <li><a href="#hreed_atlas">Hreed and Atlas</a></li>
                </ul>
              </li>
              <li><a href="#gem_data">GEM data</a></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>

import { getExpLvlLegend } from '../expression-sources/hpa';

export default {
  name: 'help',
  methods: {
    getExpLvlLegend,
  },
};
</script>

<style lang="scss">

.help-div {
  .menu-list {
    li {
      a {
        padding-top: 0;
        padding-bottom: 0;
        padding-left: 0.2em;
      }
      ul {
        margin-top: 0;
        margin-bottom: 0;
        margin-left: 0.2em;
      }
    }
  }

  #help-sidebar {
    position: fixed;
    right: 30px;
    top: 110px;
  }
}

</style>
