<template>
  <!-- eslint-disable max-len -->
  <section class="section extended-section">
    <div class="container is-fullhd">
      <h3 class="title is-3">Documentation</h3>
      <br>
      <div class="columns is-variable is-8">
        <div class="column is-narrow">
          <aside class="menu">
            <p class="menu-label">
              Table of Contents
            </p>
            <ul class="menu-list">
              <li>
                <a href="#GEM-Browser">
                  <span class="icon pr-5 has-text-info"><i class="fa fa-table"></i></span>
                  <b>GEM Browser</b>
                </a>
                <ul class="menu-list">
                  <li><a href="#reaction-page">Reaction page</a></li>
                  <li><a href="#GEM-Browser-Metabolite">Metabolite page</a></li>
                  <li><a href="#gene-page">Gene page</a></li>
                  <li><a href="#subsystem-page">Subsystem page</a></li>
                  <li><a href="#compartment-page">Compartment page</a></li>
                </ul>
                <a href="#Map-Viewer">
                  <span class="icon pr-5 has-text-info"><i class="fa fa-map-o"></i></span>
                  <b>Map Viewer</b>
                </a>
                <ul class="menu-list">
                  <li><a href="#2D-Viewer">2D Viewer</a></li>
                  <li><a href="#3D-Viewer">3D Viewer</a></li>
                  <li><a href="#Data-overlay">Data Overlay</a></li>
                </ul>
                <a href="#Interaction-Partners">
                  <span class="icon pr-5 has-text-info"><i class="fa fa-connectdevelop"></i></span>
                  <b>Interaction Partners</b>
                </a>
                <ul class="menu-list">
                  <li><a href="#Interaction-Partners-Export">Export graph</a></li>
                  <li><a href="#Interaction-Partners-Highlights">Highlights</a></li>
                  <li><a href="#Interaction-Partners-Reactions">Reactions table</a></li>
                </ul>
                <a href="#Search">
                  <span class="icon pr-5 has-text-info"><i class="fa fa-search"></i></span>
                  <b>Search</b>
                </a>
                <ul class="menu-list">
                  <li><a href="#Quick-search">Quick search</a></li>
                  <li><a href="#Global-search">Global search</a></li>
                </ul>
                <a href="#GEM">
                  <span class="icon pr-5 has-text-info"><i class="fa fa-files-o"></i></span>
                  <b>GEM</b></a>
                <ul class="menu-list">
                  <li><a href="#Integrated-models">Integrated models</a></li>
                  <li><a href="#Repository">Repository</a></li>
                  <li><a href="#Comparison">Comparison</a></li>
                  <li><a href="#FTP-access">FTP access</a></li>
                </ul>
              </li>
              <li>
                <a href="#Resources">
                  <span class="icon pr-5 has-text-info"><i class="fa fa-cogs"></i></span>
                  <b>Resources</b></a>
                <ul class="menu-list">
                  <li><a href="#API">API</a></li>
                </ul>
              </li>
            </ul>
          </aside>
        </div>
        <div id="documentation" class="column content has-text-justified">
          <p>Metabolic Atlas allows to vizualization of the content of the integrated <a href="#Integrated-models">Genome-scale metabolic models (GEMs)</a> by using the <a href="#GEM-Browser">GEM Browser</a> tool, and enables navigation of the metabolic network maps via the <a href="#Map-Viewer">Map viewer</a> tool. Moreover, interactions betweeen metabolites and genes can be explored with the <a href="#Interaction-Partners">Interaction Partners</a> tool. These three tools are available upon selecting one of the integrated models. The selected model is indicated to the right of the Metabolic Atlas logo in the top navigation bar. Leaving the <i>Explore</i> section (or the <i>GEM Browser</i> / <i>Map Viewer</i> tools) will unselect the model, and remove its name from the navigation bar.</p>
          <p>To read more details about each of the integrated models, visit the <router-link :to="{ name: 'gems', hash: '#Integrated-models'}">GEM Repository</router-link> page.</p>

          <hr class="mt-6">
          <h4 id="GEM-Browser" class="is-info is-size-4">
            <span class="icon pr-5 is-large has-text-info"><i class="fa fa-table"></i></span>
            GEM Browser
          </h4>
          <p>The <i>GEM Browser</i> is a set of dedicated pages for various components, i.e., reactions, metabolites, genes, subsystems and compartments of the selected model, which is indicated on the left side of the top navigation bar. Each page contains a button on the right to <i>Report an issue</i>. Click this button to report a problem or ask questions to the modellers.</p>

          <h5 id="reaction-page" class="is-size-5">Reaction page</h5>
          <p>The <i>Reaction</i> page shows the information about the currently selected reaction. If provided by the modellers, a list of identifiers from external databases and a list of references (PMIDs) are also shown in the <i>References</i> table below. On the right side of the page there is a list of links pointing to 2D or 3D <a href="#Map-Viewer">Map Viewer</a> pages in which this reaction is involved.</p>

          <h5 id="metabolite-page" class="is-size-5">Metabolite page</h5>
          <p>The <i>Metabolite</i> page shows information of the currently selected metabolite. Metabolites in GEMs are often differentiated according to their cell compartment localization. For this reason, one metabolite, e.g. cholesterol, may correspond to several different metabolite entries in a GEM, such as cholesterol[c], cholesterol[m], with the suffix indicating the compartment in which the metabolite is localized.</p>
          <p>The top table pf the page contains basic information extracted from the GEM. If provided, additional identifiers from external databases will also be shown in the <i>External databases</i> table under the top table.</p>
          <p>Below the <i>External databases</i> table comes the <i>Reactions</i> table. It lists all reactions involving the current metabolite as a reactant or product. The current metabolite is highlighted in black in the reaction equations. This table can be exported by clicking the button <i>Export to TSV</i>. Since metabolites are specific to a cell compartment, only reactions involving the metabolite in its specific compartment are displayed. To remove this restriction and display additional reactions involving the metabolite in any compartment, click the button to <i>See reactions from all compartments</i>. Note that the number of retrieved reactions is limited to 200. It is recommended to use the <a href="#API">API</a> to retrieve all reactions.</p>
          <p>On the top right of the page, the <a href="#Interaction-Partners">Interaction Partners</a> tool for that metabolite can be accessed by clicking the button <i>Interaction Partners</i>. Below this button there is a widget to access the corresponding 2D or 3D <a href="#Map-Viewer">Map Viewer</a> pages for this metabolite.</p>

          <h5 id="gene-page" class="is-size-5">Gene page</h5>
          <p>The layout of the Gene page is the same as the <a href="#GEM-Browser-Metabolite">Metabolite</a> page except that the top table shows the information about the currently selected gene. </p>

          <h5 id="subsystem-page" class="is-size-5">Subsystem page</h5>
          <p>The layout of the <i>Subsystem</i> page is also similar to the <a href="#GEM-Browser-Metabolite">Metabolite</a> page except that the top table shows information on the current selected metabolic subsystem instead of metabolites. In addition, the maximum number of reactions shown in the <i>Reactions</i> tables is limited to 1000 instead of 200.</p>
          <p>Subsystems correspond to a set of reactions that share a similar metabolic function. Unlike a metabolic pathway, the reactions comprising a subsystem are not necessarily linked into a completely connected network.</p>
          <p>The lists of metabolites and genes contained within the current subsystem are shown in the top table, but are restricted to a maximum of 1000 for each category. Use the <a href="#API">API</a> to retrieve a complete set of metabolites and genes for the selected subsystem. Note that, in some GEMs, a given reaction can be associated with multiple subsystems.</p>

          <h5 id="compartment-page" class="is-size-5">Compartment page</h5>
          <p>The <i>Compartment</i> page shows the information of the currently selected compartment. It is only the number of metabolites, genes and reactions is shown in the top table. To retrieve a full list of metabolites, genes and reactions for a comparment, the use of the <a href="#API">API</a> is advised. Similarly to the <a href="#GEM-Browser-Metabolite">Metabolite</a> page the list of links to the 2D or 3D Map Viewer pages where this compartment can be visualized is displayed on the right side of the page.</p>


          <hr class="mt-6">
          <h4 id="Map-Viewer" class="is-size-4">
            <span class="icon pr-5 is-large has-text-info"><i class="fa fa-map-o"></i></span>
            Map Viewer
          </h4>
          <p>The <i>Map Viewer</i> is, similar to the <a href="#GEM-Browser">GEM Browser</a>, accessible after an integrated model has been selected. It includes a 2D viewer to vizualize metabolic maps in SVG format, and a 3D viewer to explore the metabolic network in 3 dimensions. One can easly go back and forth between the <i>GEM Browser</i> and <i>Map Viewer</i> by clicking the button <i>GEM Browser</i> in the left sidebar of the <i>Map Viewer</i> page and links of the <i>Map Viewer</i> panel on the right side of the <i>GEM Browser</i> page, respectively.</p>
          <p>To switch between 2D maps and 3D networks, use the <i>Switch to 2D</i> or <i>Switch to 3D</i> button in the top left of the map, respectively. This button is disabled for a model without 2D maps, or when the corresponding 2D version of a 3D network is not available. One can select which compartment or subsystem to be shown in the viewer by clicking a corresponding item on the left sidebar.</p>

          <h5 id="2D-Viewer" class="is-size-5">2D Viewer</h5>
          <p>The 2D maps in SVG format are provided for integrated GEMs. They represent either a cell compartment or a subsystem/pathway. While a very high percentage of the reactions in the model are represented on the 2D maps, some may be unavailable. SVG maps were produced with <a target="_blank" href="https://www.omix-visualization.com/">Omix Vizualization</a>, a customizable tool for editing biochemical networks. A custom plug-in was developed to enable the creation of compact maps with consistent layout.</p>
          <p>There are five buttons on the top left of the map that allow to (from top to bottom) zoom in, zoom out, show/hide genes, show/hide subsystems, toggle fullscreen (exit the fullscreen mode with the key <i>Esc</i>), and download the SVG map on the current view. One can interact with the map by clicking and dragging the mouse to pan the view or using the mouse wheel to zoom in/out.</p>
          <p>A search function is available for 2D maps using the search bar. The window will zoom and center on each component found. Click the <i>Highlight</i> button to color all found components on the maps in red. To remove the highlight, simply clear the search bar.</p>
          <p>The SVGs are interactive; click on a node (metabolite, reaction, gene) or a subsystem to load some of its information in the sidebar. Additonal information on the corresponding selected element can be accessed by clicking the button "GEM browser" under information panel of the selected element on the left sidebar.</p>

          <h5 id="3D-Viewer" class="is-size-5">3D Viewer</h5>
          <p>The 3D renderings of the metabolic network are automatically generated from the GEM data, with the help of <a href="https://github.com/MetabolicAtlas/3d-network-viewer" target="_blank">a force-directed graph JavaScript library</a>. This 3D graph contains all the reactions in the model, grouped by cellular compartment or subsystem.</p>
          <p>There are six buttons on the top left of the 3D graph that allow one to (from top to bottom) zoom in, zoom out, show/hide genes and their connections, show/hide labels, toggle daylight/night mode, and toggle fullscreen (exit the fullscreen mode with the key <i>Esc</i>). </p>
          <p>One can interact with the 3D graph using mouse by holding left-clicking button and moving the mose to rotate the view, holding the right-clicking button and moving the mouse to pan, and scrolling the mouse wheel to zoom in/out.</p>
          <p>One can also hover a node to view its name/id or left-clik on a node (once the graph has stopped moving) to display some of its information in the left sidebar. Additonal information of the selected element can be accessed by clicking the button <i>GEM Browser</i> under the information panel of the selected element on the left sidebar.</p>
          <p>One can search for a specific item with id, name or alias by using the search bar on top of the 3D graph. The view will be zoomed in and centered on one of the found components, and the centered component will be highlighted in red square. In case there are more than one found components, one can change the view to each found component by clicking the left/right buttons on the right side of the search bar. When changing to the next found component, the view will be re-centered to the new component. </p>
          <p>Similar to the 2D SVG maps, the 3D graphs are interactive. Clicking a node on the 3D grap, be it a metabolite, reaction, or gene, the information panel on the left sidebar will be updated for the clicked node. Additonal information of the selected node can be accessed by clicking the button "GEM Browser" under information panel on the left sidebar.</p>

          <h5 id="Data-overlay" class="is-size-5">Data overlay</h5>
          <div class="columns ml-0">
            <div class="column pl-0 is-8 content">
              <p>The <i>Data overlay</i> panel is by default hidden in the <i>Map Viewer</i>. By clicking the <i>Data overlay</i> button on the right side of the page, one can toggle the hidden/display of this panel. On the <i>Data overlay</i> panel, gene expression levels for genes from <a href="https://www.proteinatlas.org/about/releases#18" target="_blank">The Human Protein Atlas v18</a> can be loaded by selecting one of the tissues in the drop down list. Once selected, the RNA levels corresponding to the chosen tissue will be used to color each gene on the respective map, according to the color legend (an example of the color legend is shown <b>Figure 1</b>). To clear the RNA levels, select the <i>None</i> option in the drop down list. RNA levels are available for both 2D and 3D Map Viewer. The data is obtained from version 18 of the Protein Atlas with the units in log<sub>2</sub>(TPM+1) associated with a gradient colorbar.</p>
              <p>If multiple data are selected in the <i>Data overlay</i> sidebar, the overlay will switch to the comparison mode, using a differently color legend (see <b>Figure 2</b>) for the log fold change between the selected data.</p>
              <p>The <i>Data overlay</i> sidebar allows uploading of the custom data in <a target="_blank" href="https://en.wikipedia.org/wiki/Tab-separated_values">TSV format</a>. If the file is parsed correctly, the file name will be highlighted in green; in case errors are detected, it will be highlighted in red. The expected custom data file should contain at least two columns with headers and using tab delimiter. The first column has to contain gene IDs, identical to the ones in the model. Any missing genes or missing values will be assigned an "n/a" value and highlighted in gray. The rest of the columns act as data series, with each column being a new data serie, as shown in the example to the right (<b>Figure 3</b>). The headers of these data series will be shown automatically in the dropdown options for the uploaded data. The values are expected in TPM.</p>
            </div>
            <div class="column">
              <RNALegend></RNALegend>
              <p style="font-size:80%"><b>Figure 1: Color legend for RNA level in Data overlay when only one data is selected.</b></p>

              <br>
              <RNALegend text="log<sub>2</sub>(TPM<sub>T2</sub>+1 / TPM<sub>T1</sub>+1)" left-value="-5" right-value="5" :gradient="`${multipleColors}`"></RNALegend>
              <p style="font-size:80%"><b>Figure 2: Color legend for RNA level in Data overlay when multiple data are selected.</b></p>

              <br>
              <blockquote>
                geneID&emsp;heart&emsp;liver<br>
                ENSG00000177666&emsp;42&emsp;8701<br>
                ENSG00000175535&emsp;572<br>
                ENSG00000187021&emsp;3498&emsp;1768
              </blockquote>
              <p style="font-size:80%"><b>Figure 3: Example file for custom data to be uploaded in Data overlay</b></p>
            </div>
          </div>


          <hr class="mt-6">
          <h4 id="Interaction-Partners" class="is-size-4">
            <span class="icon pr-5 is-large has-text-info"><i class="fa fa-connectdevelop"></i></span>
            Interaction Partners
          </h4>
          <div id="interaction-partners-intro">
            <figure id="interaction-partners-video">
              <video poster="@/assets/interPart-cover.jpg" playsinline controls muted loop>
                <source src="@/assets/interPart.mp4" type="video/mp4">
              </video>
              <figcaption>Demo of the interaction partners tool</figcaption>
            </figure>
            <div>
              <p>For a given metabolite or gene, this tool (shown in the demo video) renders a connected graph of the other metabolites and genes with which it interacts via shared reaction(s). The metabolite or gene of interest is centered on the graph. Connectivity is determined based on the reactions with which this metabolite or gene is associated, i.e. an edge between two nodes may represente a connections that occurs in multiple reactions. For medium-sized networks of interaction partners, there is a prompt before generating the graph. For very large networks (e.g. for H<sub>2</sub>O) the graph will not be generated. One can left-click a node to display a context menu with 3 options:</p>
              <ul>
                <li>Load interaction partners: reload the interaction partners graph with the clicked node as the new central node.</li>
                <li>Expand interaction partners: add additional interaction partner nodes for the clicked node to the graph. Expanded interactions are represented with dashed lines.</li>
                <li>Highlight reaction: some nodes may be involved in many different reactions. Select a reaction from the list to show the other interaction partners associated with the selected reaction (other interaction partners will be grayed-out). The directionality of each edge is indicated as a triangle, or diamonds in case of reversible reactions. To remove the highlight, click on the <span><i class="fa fa-eraser"></i></span> eraser button at the top of the graph.</li>
              </ul>
            </div>
          </div>
          <br>
          <p>Clicking/selecting a node (shown as black colored node) also shows links on the right sidebar to quickly reset the <i>Interaction Partners</i> for that node or navigate to the corresponding <a href="#GEM-Browser">GEM Browser</a> page.</p>
          <p>The top-left buttons on the graph allow one to (from left to right): customize the graph node's shape and colors, zoom in, zoom out, reset the display, reload the graph (remove expanded interaction partners), and remove any highlighting. The nodes can also be moved around the graph after selection.</p>
          <p>If available, expression levels from the <a href="https://www.proteinatlas.org/">Human Protein Atlas</a> can be enabled and applied on the <i>Interaction Partners</i> graph with the panel on the top right, by selecting one of the tissues in the drop down list. The action will update the color of gene's nodes according to the legend. Some genes may not have RNA levels available in Human Protein Atlas, and in such case their color corresponds to the n/a color.</p>

          <h5 id="Interaction-Partners-Export" class="is-size-5">Export graph</h5>
          The graph of <i>Interaction Partners</i> can be exported by clicking the button <i>Export graph</i>. There are two options of graph exporting: GraphML Interaction-Partners PNGhML is a Cytoscape compatible format. Currently, color format is not supported for the GraphML option.

          <h5 id="Interaction-Partners-Highlights" class="is-size-5">Highlights</h5>
          <p>Nodes may belong to multiple compartments and/or subsystems. The filter box enables highlighting (red label color) the nodes belonging to a given subsystem or compartment. The two filters are additive. Enzymes may catalyze reactions in differents compartments / subsystems; label of genes that encode such enzymes are highlighted in orange on the graph.</p>

          <h5 id="Interaction-Partners-Reactions" class="is-size-5">Reactions table</h5>
          <p>Information of the reactions are listed in <i>Reactions</i> table which is located on the lower part of the page. Selecting a label of metabolite or gene in the table will select the corresponding node on the graph, and vice versa. Selecting a reaction ID label highlight the reaction on the graph. The search bar above the table can be used to filter out rows to find a given component. This table can be exported by clicking the button <i>Export to TSV</i>.</p>


          <hr class="mt-6">
          <h4 id="Search" class="is-size-4">
            <span class="icon pr-5 is-large has-text-info"><i class="fa fa-search"></i></span>
            Search
          </h4>
          <p>For convenience, Metabolic Atlas provides two ways of searching: <i>Quick search</i> and <i>Global search</i>. One can search for any terms in metabolites, genes, reactions, subsystems or compartments information with both searching methods. In addition, proximity searching is enabled so that the searching algorithm will not only search for exact matching of the input keywords but also try to find hits that are similar to the input keywords.</p>

          <h5 id="Quick-search" class="is-size-5">Quick search</h5>
          <p>By clicking the icon <span><i class="fa fa-search"></i></span> in the top navigation bar, one can perform a quick search of any terms in metabolites, genes, reactions, subsystems or compartments. The found hits will be shown directly under the searching bar if there is any or prompted with <i>No matches</i>. The results links redirect to the corresponding <i>GEM Browser</i> page of the component clicked. One can also click the icon <span><i class="fa fa-table"></i></span> or <span><i class="fa fa-connectdevelop"></i></span> to the left of each found hit to redirect to the <i>Metabolite</i> page or <i>Interaction Parters</i> page respectively.</p>
          <p>The <i>Quick search</i> is restricted to the selected GEM on the left side of searching bar and limited to 50 results per component type. Alternatively, one can click on the banner under the search input field to run a <i>Global Search</i>, where the term is searched among all the integrated models' components and is unrestricted. To learn more about the search term possiblities, go to the <a href="#Global-Search">Global Search</a> section of this page.</p>

          <h5 id="Global-search" class="is-size-5">Global search</h5>
          <p>The <i>Global search</i> page queries all the integrated metabolic models. Each metabolic component has its own results table accessible via the dedicated tab. Tabs are inactivated when no results are found. The search text is not restricted to the visible columns; for example, searching an MetaNetX ID will return results for the metabolites and/or reactions matching the ID even though the MetaNetX column is not in the table. The search algorithm matches partial names of components: searching for 'cholesterol' will output all metabolites containing the substring 'cholesterol'. When the name of a metabolite is provided, all metabolites matching or partially matching this name be returned, in addition to a the list of all reactions that involve these matching metabolites.</p>


          <hr class="mt-6">
          <h4 id="GEM" class="is-size-4">
            <span class="icon pr-5 is-large has-text-info"><i class="fa fa-files-o"></i></span>
            GEM
          </h4>
          <p>A genome-scale metabolic model (GEM) is a mathematical representation of a metabolic reaction network.</p>

          <h5 id="Integrated-models" class="is-size-5">Integrated GEMs</h5>
          <p>Currently, Metabolic Atlas contains seven integrated models, i.e., <i>Fruitfly-GEM</i>, <i>Human-GEM</i>, <i>Mouse-GEM</i>, <i>Rat-GEM</i>, <i>Worm-GEM</i>, <i>Yeast-GEM</i> and <i>Zebrafish-GEM</i>. Details can be found at the <router-link :to="{ name: 'gems', hash: '#Integrated-models'}">GEM Repository</router-link> page.</p>

          <h5 id="Repository" class="is-size-5">GEM Repository</h5>
          <p>The repository lists all models constructed by the SysBio research group; this includes older models that may no longer be maintained (for example HMR 2.0), and others that were recently published. The more recent GEMs can also be found in the <a href="https://www.github.com/SysBioChalmers/" target="_blank">SysBioChalmers organization GitHub</a>.</p>
          <p>Click on a row in the table to show more information about a GEM. One can download models in various file formats (when available).</p>

          <h5 id="Comparison" class="is-size-5">Comparison</h5>
          <p>In the first section of the page one can select 2 or 3 integrated GEMs to compare. The comparison is performed dynamically, by inspecting the external identifiers in the database. If a reaction or a metabolite share at least one such external identifier, they are considered to be shared between the compared models. Otherwise, they are considerend to be unique to the respective model. The comparison table is interactive - by clicking on a cell, the corresponding comparison details are shown on the right panel.</p>
          <p>In the second section, the <i>Comparison</i> page provides statistics about the comparison/overlap between Human-GEM 1.0.2 and HMR 2.0, as well as Human-GEM and Recon3D. This comparison has been performed manually for an early verion of Human-GEM, and will not be updated.</p>

          <h5 id="FTP-access" class="is-size-5">FTP access</h5>
          <p>Genome-Scale Metabolic model files can be downloaded from <a :href="`ftp://${ftpUrl}/`">ftp://{{ ftpUrl }}</a> or by connecting to the FTP using your favorite FTP client (e.g. <a href="https://filezilla-project.org/">FileZilla</a>).</p>
          <span class="has-text-weight-bold lab">Host:</span> <a :href="`ftp://${ftpUrl}/`"> ftp://{{ ftpUrl }}</a><br>
          <span class="has-text-weight-bold lab">Login:</span> leave blank<br>
          <span class="has-text-weight-bold lab">Password:</span> leave blank<br>
          <span class="has-text-weight-bold lab">Port:</span> 21

          <hr class="mt-6">
          <h4 id="Resources" class="is-size-4">
            <span class="icon pr-5 is-large has-text-info"><i class="fa fa-cogs"></i></span>
            Resources
          </h4>
          <p>Lists of the most relevant software tools, algorithms, or databases published by the SysBio group.</p>

          <h5 id="API" class="is-size-5">API</h5>
          <p>Metabolic Atlas has a <a href="/api/v2/" target="_blank">dedicated interface to facilite the use of the API</a>, with output provided in JSON format. When using this service, kindly use a limit of 10 requests per second. The API is still undergoing development; while it is covers the entire content of the models, it might change without prior notice.</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>

import RNALegend from '@/components/explorer/mapViewer/RNALegend.vue';
import { multipleColors } from '@/expression-sources/hpa';

export default {
  name: 'Help',
  components: {
    RNALegend,
  },
  data() {
    return {
      multipleColors,
      ftpUrl: 'ftp.metabolicatlas.org',
    };
  },
};
</script>

<style lang="scss" scoped>
  .menu-list {
    ul {
      margin-top: 0;
    }
  }

  #interaction-partners-intro {
    display: flex;
    flex-direction: column-reverse;
  }

  #interaction-partners-video {
    margin: 1rem 0;

    figcaption {
      font-size: 80%;
      font-weight: bold;
      font-style: normal;
    }
  }

  @media screen and (min-width: $tablet) {
    #interaction-partners-intro {
      display: block;
    }

    #interaction-partners-video {
      float: right;
      width: 50%;
      margin: 0 0 1rem 1.5rem;
    }
  }
</style>
