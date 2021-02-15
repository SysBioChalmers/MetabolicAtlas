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
                  <li><a href="#metabolite-page">Metabolite page</a></li>
                  <li><a href="#gene-page">Gene page</a></li>
                  <li><a href="#subsystem-page">Subsystem page</a></li>
                  <li><a href="#compartment-page">Compartment page</a></li>
                  <li><a href="#GEM-Browser-Search">Search</a></li>
                </ul>
                <a href="#Interaction-Partners">
                  <span class="icon pr-5 has-text-info"><i class="fa fa-connectdevelop"></i></span>
                  <b>Interaction Partners</b>
                </a>
                <ul class="menu-list">
                  <li><a href="#IP-Search">Search</a></li>
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
                <a href="#Global-search">
                  <span class="icon pr-5 has-text-info"><i class="fa fa-search"></i></span>
                  <b>Global search</b>
                </a>
                <a href="#GEMs"><b>GEMs</b></a>
                <ul class="menu-list">
                  <li><a href="#Integrated-models">Integrated models</a></li>
                  <li><a href="#Repository">Repository</a></li>
                  <li><a href="#Comparison">Comparison</a></li>
                  <li><a href="#FTP-download">FTP download</a></li>
                </ul>
              </li>
              <li>
                <a href="#Resources"><b>Resources</b></a>
                <ul class="menu-list">
                  <li><a href="#API">API</a></li>
                </ul>
              </li>
            </ul>
          </aside>
        </div>
        <div id="documentation" class="column content has-text-justified">
          Metabolic Atlas allows users to vizualize the content of the integrated <a href="#Integrated-models">Genome-scale metabolic models (GEMs)</a> by using the <a href="#GEM-Browser">GEM Browser</a> tool, and enables navigation of the metabolic network maps via the <a href="#Map-Viewer">Map viewer</a> tool. These two tools are available upon selecting one of the integrated models. The selected model is indicated to the right of the Metabolic Atlas logo in the top navigation bar. Leaving the <i>Explore</i> section (or the <i>GEM Browser</i> / <i>Map Viewer</i> tools) will unselect the model, and remove its name from the navigation bar.<br>
          To browse our integrated GEMs, visit the <router-link :to="{ name: 'gems'}">GEM Repository</router-link> page.<br>
          The <i>GEM Browser</i> and the <i>Map Viewer</i> are closely connected, and users can navigate between the two tools using the buttons in the top navigation bar.

          <hr class="mt-6">
          <h4 id="GEM-Browser" class="is-info is-size-4">
            <span class="icon pr-5 is-large has-text-info"><i class="fa fa-table"></i></span>
            GEM Browser
          </h4>
          The <i>GEM Browser</i> is a set of dedicated pages for different components of the model; reactions, metabolites, genes, subsystems, and compartments. Each of these pages contains a button on right, to report a problem or ask questions to the modellers.

          <h5 id="reaction-page" class="is-size-5">Reaction page</h5>
          This page shows information about the current selected reaction. If provided by the modellers, a list of identifiers from external databases and a list of references (PMIDs) are also shown in the Reference table below.<br>
          On the right of the page, the list of maps/networks where this reaction can be vizualize - in context with other reactions - is displayed. Users are redirected to the <i>Map Viewer</i> tool when clicking on one of the map name; to return back to the <i>GEM Browser</i>, click the <i>GEM Browser</i> button in the top navigation bar.

          <h5 id="metabolite-page" class="is-size-5">Metabolite page</h5>
          The Metabolite page shows information on the current selected metabolite. Metabolites in GEMs are often differentiated according to their cell compartment localization (e.g., endoplasmic reticulum). For this reason, one metabolic species, e.g. cholesterol, may correspond to several different metabolite entries in a GEM, such as cholesterol[c], cholesterol[m], etc. (the suffix indicates the compartment in which the metabolite is localized).<br>
          The top table contains basic information extracted from the GEM. If provided, additional identifiers from external databases will be shown in the External IDs table below.<br>
          On the right side of the page, users can access the <a href="#Interaction-Partners">Interaction Partners</a> tool for the metabolite.

          <h6 class="has-text-grey">Reactions table</h6>
          Lists all the reactions involving the current metabolite as a reactant or a product. The current metabolite is denoted with a black text color in the reaction equations. Since metabolites are specific to a cell compartment, only reactions involving the metabolite in its specific compartment are displayed. To remove this restriction and display additional reactions involving the metabolite in any compartment, click the <i>Expand to all compartments</i> button.<br>
          Note that the number of reactions is limited to 200; to retrieve all the reactions we invite users to use the <a href="#API">API</a>.

          <h5 id="gene-page">Gene page</h5>
          Shows information about the current selected gene. The top table contains basic information extracted from the GEM. If provided, additional identifiers from external databases will be shown in the external IDs table.<br>On the right side of the page, users can access the <a href="#Interaction-Partners">Interaction Partners</a> tool for this gene.

          <h6 class="has-text-grey">Reactions table</h6>
          Lists all the reactions catalyzed by the enzyme encoded by the current gene.<br>
          Note that the number of reactions is limited to 200; to retrieve all the reactions we invite users to use the <a href="#API">API</a>.

          <h5 id="subsystem-page" class="is-size-5">Subsystem page</h5>
          This page shows information on the current selected metabolic subsystem. Subsystems correspond to a set of reactions that share a similar metabolic function. Unlike a metabolic pathway, the reactions comprising a subsystem are not necessarily linked into a completely connected network.<br>
          the lists of metabolites and genes contained within the current subsystem are shown in the table, but are restricted to a maximum of 1000 for each category. Use the <a href="#API">API</a> to retrieve the complete set of metabolites and genes for the selected subsystem.<br>On the right of the page, the list of maps/networks where this subsystem can be vizualize is displayed. Users are redirected to the <i>Map Viewer</i> tool when clicking on one of the map name.

          <h6 class="has-text-grey">Reactions table</h6>
          Shows all the reactions that belong to the current subsystem. Note that in some GEMs, a given reaction can be associated with multiple subsystems.
          The number of reactions shown is limited to 1000; to retrieve all associated reactions we invite users to use the <a href="#API">API</a>.

          <h5 id="compartment-page" class="is-size-5">Compartment page</h5>
          Shows information on the current selected compartment. The full list of metabolites, genes and reactions is available through the <a href="#API">API</a>.<br>Similarly to the subsystem page the list of maps/networks where this compartment can be vizualize is displayed on the right.

          <h5 id="GEM-Browser-Search" class="is-size-5">GEM Browser Search</h5>
          Search for any term in metabolites, genes, reactions, subsystems, or compartments information. The results links redirect to the corresponding <i>GEM Browser</i> page of the component clicked.<br>
          The <i>GEM Browser</i> search is restricted to the selected GEM and limited to 50 results per component type. Alternatively, users can click on the banner under the search input field to run a <i>Global Search</i>, where the term is searched among all the integrated models' components and is unrestricted. To learn more about the search term possiblities, go to the <a href="#Global-Search">Global Search</a> section of this page.

          <hr class="mt-6">
          <h4 id="Interaction-Partners" class="is-size-4">
            <span class="icon pr-5 is-large has-text-info"><i class="fa fa-connectdevelop"></i></span>
            Interaction Partners
          </h4>
          For a given metabolite or gene, this tool renders a connected graph of the other metabolites and genes with which it interacts via shared reaction(s). The metabolite or gene of interest is centered on the graph. Connectivity is determined based on the reactions with which this metabolite or gene is associated, i.e. a edge between two nodes maybe represente a connections that occurs in multiple reactions. For medium-sized networks of interaction partners, the user is prompted before generating the graph. For very large networks (e.g. for H<sub>2</sub>O) the graph will not be generated. Users can left-click a node to display a context menu with 3 options:<br>
          <ul>
            <li>Load interaction partners: reload the interaction partners graph with the clicked node as the new central node.</li>
            <li>Expand interaction partners: add additional interaction partner nodes for the clicked node to the graph. Expanded interactions are represented with dashed lines.</li>
            <li>Highlight reaction: some nodes may be involve in many different reactions. Select a reaction from the list to show the other interaction partners associated with the selected reaction (other interaction partners will be grayed-out). The directionality of each edge is indicated as a triangle, or diamonds in case of reversible reactions. To remove the highlight, click on the "eraser" button at the top of the graph.</li>
          </ul>
          Clicking/selecting a node (shown as black colored node) also shows links on the right sidebar to quickly reset the <i>Interaction Partners</i> for that node or the navigate to its <a href="#GEM-Browser">GEM Browser</a> page.
          The top-left buttons allow users to (from left to right): customize the graph node's shape and colors, zoom in, zoom out, reset the display, reload the graph (remove expanded interaction partners), and remove any highlighting. The nodes can also be moved around the graph after selection.
          If available, expression levels from the Human Protein Atlas can be enabled and applied on the <i>Interaction Partners</i> graph using the panel on the top-right button. Doing so, will update the gene's node colors according to the legend. Some genes may not have RNA levels available - in such case their color corresponds to the n/a color.

          <h6 class="has-text-grey">Export graph</h6>
          Clicking the <i>Export graph</i> button will display two options: GraphML or PNG. GraphML is a Cytoscape compatible format; currently, the colors are not exported in this format.

          <h6 class="has-text-grey">Highlights</h6>
          Nodes may belong to multiple compartments and/or subsystems. The filter box allows users to highlight (red label color) the nodes belonging to a given subsystem or compartment. The two filters are additive. Enzymes may catalyze reactions in differents compartments / subsystems; label of genes that encode such enzymes are highlighted in orange on the graph.

          <h6 class="has-text-grey">Reactions table</h6>
          Information of the reactions are listed in this table. Selecting a label of metabolite or gene in the table will select the corresponding node on the graph, and vice versa. Selecting a reaction ID label highlight the reaction on the graph. The search bar above the table can be used to filter out rows to find a given component. The table can be exported via the "Export to TSV" button.

          <h5 id="IP-Search" class="is-size-5">Interaction Partners Search</h5>
          Search for any term in metabolites or genes information. The results links redirect to the corresponding <i>Interaction Partners</i> page of the component clicked.<br>
          The <i>Interaction Partners</i> search is also restricted to the selected GEM and limited to 50 results per component type.

          <hr class="mt-6">
          <h4 id="Map-Viewer" class="is-size-4">
            <span class="icon pr-5 is-large has-text-info"><i class="fa fa-map-o"></i></span>
            Map Viewer
          </h4>
          The <i>Map Viewer</i> is - similar to the <i>Interaction Partners</i> and the <i>GEM Browser</i> - a separate tool, accessible after an integrated model has been selected. It includes a 2D viewer to vizualize metabolic maps in SVG format, and a 3D viewer to explore the metabolic network in 3 dimensions. Users can easly toggle between the <i>GEM Browser</i> and <i>Map Viewer</i> using the buttons in the top navigation bar.<br>
          To switch between 2D maps and 3D network, use the "Switch to 2D" or "Switch to 3D" button in the top left of the map, respectively. This button is disabled for a model without 2D maps, or when the corresponding 2D version of a 3D network is not available. The two left sidebar buttons are used to select which compartment or subsystem will be shown in the viewer.

          <h5 id="2D-Viewer" class="is-size-5">2D Viewer</h5>
          2D SVG maps are provided for integrated GEMs. They represent either a cell compartment or a subsystem/pathway. While a very high percentage of the reactions in the model are represented on the 2D maps, some may be unavailable. SVG maps were produced with <a target="_blank" href="https://www.omix-visualization.com/">Omix</a>, a customizable tool for editing biochemical networks. A custom plug-in was developed to enable the creation of compact maps with consistent layout.<br><br>
          Three buttons on the top left of the UI allow users to zoom in, zoom out and show/hide the genes on the current map.<br>
          Users can interact with the maps by clicking and dragging the mouse to pan the view or using the mouse wheel to zoom in/out.<br>
          A search function is available for 2D maps using the search bar. The window will zoom and center on each component found. Click the 'highlight' button to color all found components on the maps in red. To remove the highlight, simply clear the search bar.<br>
          The SVGs are interactive; click on a node (metabolite, reaction, gene) or a subsystem to load some of its information in the sidebar. Additonal information on the corresponding selected element can be accessed by clicking the <i>GEM Browser</i> button.<br>

          <h5 id="3D-Viewer" class="is-size-5">3D Viewer</h5>
          3D renderings of the metabolic network are automatically generated from the GEM data, with the help of <a href="https://github.com/vasturiano/3d-force-graph" target="_blank">a force-directed graph JavaScript library</a>. This 3D graph contains all the reactions in the model, grouped by cellular compartment or subsystem.<br><br>
          Interaction with the 3D graph is possible using the mouse by holding left-click and moving the mose to rotate the view, right-click to pan, and use the mouse wheel to zoom in/out.
          Users can also hover a node to view its name/id or left-clik on a node (once the graph has stopped moving) to display some of its information in the sidebar. Additonal information on the corresponding selected element can be accessed by clicking the <i>GEM Browser</i> button.<br>

          <h5 id="Data-overlay" class="is-size-5">Data overlay</h5>
          <div class="columns m-0">
            <div class="column p-0 is-8 content">
              Gene expression levels for genes from <a href="https://www.proteinatlas.org/about/releases#18" target="_blank">The Human Protein Atlas v18</a> can be loaded using the <i>Data overlay</i> sidebar on the right side. Once selected, the RNA levels corresponding to the chosen tissue will be used to color each gene on the respective map, as shown in the legend. To clear the RNA levels, select the <i>None</i> option. RNA levels are available for both the 2D and 3D Map Viewer. The data is obtained from version 18 of the Protein Atlas with the units in log<sub>2</sub>(TPM+1) associated with a gradient colorbar.<br>
              The <i>Data overlay</i> sidebar allows for the upload of user-generated data in TSV format. If the file is parsed correctly, the file name will be highlighted green; in case errors are detected, it will be highlighted red. The expected format is at least two columns with headers using tab delimiters. For an exact description of the TSV file format <a target="_blank" href="https://en.wikipedia.org/wiki/Tab-separated_values">see the Wiki page</a>. The first column has to contain the gene IDs, identical to the ones in the model. Any missing genes or missing values will be assigned an "n/a" value and highlighted in gray. The rest of the columns act as data series, with each column being a new series, as shown in the example to the right. The headers of these data series will be shown automatically in the dropdown options for the uploaded data. The values are expected in TPM.<br>
              If multiple data are selected in the <i>Data overlay</i> sidebar, the overlay will switch to the comparison mode, using a differently colored legend for the log fold change between the selected data.<br>
            </div>
            <div class="column">
              <blockquote>
                geneID&emsp;heart&emsp;liver<br>
                ENSG00000177666&emsp;42&emsp;8701<br>
                ENSG00000175535&emsp;572<br>
                ENSG00000187021&emsp;3498&emsp;1768
              </blockquote>
              <RNALegend></RNALegend>
              <br>
              <RNALegend text="log<sub>2</sub>(TPM<sub>T2</sub>+1 / TPM<sub>T1</sub>+1)" left-value="-5" right-value="5" :gradient="`${multipleColors}`"></RNALegend>
            </div>
          </div>

          <hr class="mt-6">
          <h4 id="Global-search" class="is-size-4">
            <span class="icon pr-5 has-text-info"><i class="fa fa-search"></i></span>
            Global search
          </h4>
          The <i>Global search</i> page queries all the integrated metabolic models. Each metabolic component has its own results table accessible via the dedicated tab. Tabs are inactivated when no results are found. The search text is not restricted to the visible columns; for example, searching an MetaNetX ID will return results for the metabolites and/or reactions matching the ID even though the MetaNetX column is not in the table. The search algorithm matches partial names of components: searching for 'cholesterol' will output all metabolites containing the substring 'cholesterol'. When the name of a metabolite is provided, all metabolites matching or partially matching this name be returned, in addition to a the list of all reactions that involve these matching metabolites. The global search is also able to query reactions in a more advanced way using special patterns:
          <ul>
            <li>Use the compartment letter at the end of a metabolite name, e.g cholesterol[c] to match metabolites associated with that compartment.</li>
            <li>Use " => " and metabolite terms - ID (m02439c), name (malate) or name with compartment (malate[c]) - in the query term to indicate that only reactions should be searched, and to return reactions involve the specified metabolite(s) as reactant/product. For example, "pyruvate =>" will return all reactions in which pyruvate participates as a reactant.</li>
            <li>Use " + " and metabolite terms - ID (m02439c), name (malate) or name with compartment (malate[c]) - to force the presence of multiple metabolites in the retrieved reactions. For example, "pyruvate + malate" returns all reactions involving at least pyruvate <b>and</b> malate.</li>
            <li>Combine the three patterns to refine the results even further.</li>
          </ul>

          <hr class="mt-6">
          <h4 id="GEMs" class="is-size-4">GEMs</h4>
          A genome-scale metabolic model (GEM) is a mathematical representation of a metabolic reaction network.

          <h5 id="Integrated-models" class="is-size-5">Integrated GEMs</h5>
          Currently, Metabolic Atlas contains two integrated models, <i>Yeast-GEM</i> and <i>Human-GEM</i>.

          <h5 id="Repository" class="is-size-5">GEM Repository</h5>
          The repository lists all models constructed by the SysBio research group; this includes older models that may no longer be maintained (for example HMR 2.0), and others that were recently published. The more recent GEMs can also be found in the <a href="https://www.github.com/SysBioChalmers/" target="_blank">SysBioChalmers organization GitHub</a>.<br>
          Click on a row in the table to show more information about a GEM. Users can download models in various file formats (when available).

          <h5 id="Comparison" class="is-size-5">Comparison</h5>
          In the first section of the page one can select 2 or 3 integrated GEMs to compare. The comparison is performed dynamically, by inspecting the external identifiers in the database. If a reaction or a metabolite share at least one such external identifier, they are considered to be the shared between the compared models. Otherwise, they are considerend to be unique to the respective model. The table with the comparison is interactive - by clicking on a cell, the comparison details are shown.<br>
          In the second section, the <i>Comparison</i> page provides statistics about the comparison/overlap between Human-GEM and HMR 2.0, and Recon3D. This comparison has been performed manually for an early verion of Human-GEM, and will not be updated.

          <h5 id="FTP-download" class="is-size-5">FTP download</h5>
          Genome-Scale Metabolic model files can be downloaded from <a :href="`ftp://${ftpUrl}/`">metabolicatlas.org</a> or by connecting to the FTP using your favorite FTP client (e.g. <a href="https://filezilla-project.org/">FileZilla</a>).

          <br>
          <span class="has-text-weight-bold lab">Host:</span> <a :href="`ftp://${ftpUrl}/`"> metabolicatlas.org</a><br>
          <span class="has-text-weight-bold lab">Login:</span> leave blank<br>
          <span class="has-text-weight-bold lab">Password:</span> leave blank<br>
          <span class="has-text-weight-bold lab">Port:</span> 21

          <hr class="mt-6">
          <h4 id="Resources" class="is-size-4">Resources</h4>
          Lists of the most relevant software tools, algorithms, or databases published by the SysBio group.

          <h5 id="API" class="is-size-5">API</h5>
          We have a <a href="/api" target="_blank">dedicated interface to facilite the use of the API</a>, with output provided in JSON format. When using this service, we kindly ask users to limit request to 10 per second. The API is still undergoing development; while it is covers the entire content of the models, it might change without prior notice.
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
      ftpUrl: process.env.VUE_APP_FTP_SERVER,
    };
  },
};
</script>

<style lang="scss" scoped>
  .menu-list > a {
    padding-left: 0;
  }
</style>
