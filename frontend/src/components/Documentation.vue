<template>
  <section class="section extended-section">
    <div class="container">
      <h2 class="title is-2">Documentation</h2>
      <br>
      <div class="columns is-variable is-8">
        <div class="column is-narrow">
          <aside class="menu">
            <p class="menu-label">
              Table of Contents
            </p>
            <ul class="menu-list">
              <li>
                <a href="#Explore"><b>Explore integrated models</b></a>
                <ul class="menu-list">
                  <li><a href="#GEM Browser">GEM Browser</a></li>
                  <ul class="menu-list">
                    <li><a href="#GEM Browser Search">Search</a></li>
                    <li><a href="#Interaction Partners">Interaction Partners</a></li>
                  </ul>
                  <li><a href="#Map Viewer">Map Viewer</a></li>
                  <ul class="menu-list">
                    <li><a href="#2D Viewer">2D Viewer</a></li>
                    <li><a href="#3D Viewer">3D Viewer</a></li>
                  </ul>
                  <li><a href="#API">API</a></li>
                  <li><a href="#Global search">Global search</a></li>
                </ul>
              </li>
              <li>
                <a href="#GEMs"><b>GEMs</b></a>
                <ul class="menu-list">
                  <li><a href="#Repository">Repository</a></li>
                  <li><a href="#Comparison">Comparison</a></li>
                  <li><a href="#FTP download">FTP download</a></li>
                </ul>
              </li>
              <li><a href="#Resources"><b>Resources</b></a></li>
              <li><a href="#Privacy"><b>Privacy statement</b></a></li>
            </ul>
          </aside>
        </div>

        <div class="column content is-medium has-text-justified">
          <h3 id="Explore">Explore integrated models</h3>
          For information which genome-scale metabolic models are integrated into the database, please refer to the <router-link :to="{ name: 'gems'}">GEMs Repository</router-link> page.

          <h4 id="GEM-Browser">GEM Browser</h4>
          <h6 id="">Metabolite page</h6>
          Show the description of the current selected metabolite. This is a combination of annotations from the model, in-house annotations, and relevant information from external sources (e.g. HMDB for human data). The same metabolite can, and often will, participate multiple times in this table as it, for example, will be produced by one reaction and then consumed by another.

          <h6 id="">Reactions table</h6>
          Here all the reactions that the current metabolite participates in, either as a reactant or a product, are listed. <br>
          Please note that a metabolite is identified by the compartment in which it is found in (the last letter of the id), therefore you will only see reactions that occur in the current compartment, <u>unless</u> you press the <i>Expand to all compartments</i> button.<br>
          <i>Please note</i> that the number of reactions will be limited to 200, no matter what.

          <h6 id="">Reaction page</h6>
          Show the description of the current selected reaction.

          <h4 id="GEM Browser Search">Search</h4>
          Search for the term in metabolites, enzymes, subsystems, reactions, and reaction components.<br>
          <u>Metabolites</u>: kegg_id, hmdb_id, hmdb_name contains <br>
          <u>Enzymes</u>: (uniprot_acc) <br>
          <u>Subsystems</u>: (name contains) <br>
          <u>Reactions</u>: (equation contains) <br>
          <u>ReactionComponent</u>: (id, short name contains, long name contains, formula contains) <br>
          Once you start typing it will pull out all possible matches from the database,           <i>for this given model</i>, and show these in the drop-down. Depending on what type of 'hit' your requests results in (metabolite, enzyme, or reaction) a number of different green buttons are shown:
          For a metabolite: <a href="#Interaction Partners">Interaction partners</a>, <a href="#metabolitepage">Metabolite page</a>.<br>
          For an enzyme: <a href="#closestpartners">Closest interaction partners</a>, <a href="#enzymepage">Enzyme page</a>.<br>
          For a reaction: <a href="#reactionpage">Reaction page</a>.<br>
          By pressing one of these you go directly to that page.<br>
          <i>alternatively</i> you can press Enter and be take to a table of all possible <a href="#searchresults">search results</a> that fit your term.

          <h4 id="Interaction Partners">Interaction Partners</h4>
          We treat all chemical equations (reactions) from Human1 as binary interactions. This gives us the option of "zooming in" around a given reaction component (gene or metabolite). <br>
          Take for example the reaction R_HRM_3905 <i>ethanol[c] + NAD+[c] => acetaldehyde[c] + H+[c] + NADH[c]</i>, modified by 9 ADH proteins, this would give a 'neighbourhood' of ethanol, NAD+, acetaldehyde, H+, NADH, ADH1B, ADH1C, ADH1A, ADHFE1, ADH7, ADH6, ADH4, ZADH2, and ADH5. But these metabolites also participate in other reactions.<br>
          This could be used to determine how important a given reaction component is, how a set of reaction components interact and how their expression levels change between tissues.<br>
          To zoom in and out, simply press either the <b>+</b> or <b>-</b> button to zoom in the graph.<br>
          Press the <b>Fit</b> button will zoom in, or out depending, to fit all the edges and nodes of the graph to the window size.

          <h6 id="">Graph customization</h6>
          It is possible to change shape and color for the proteins and the metabolites shown in the graph. This is done by pressing the <b>Options</b> button.<br>
          Here you are presented with a number of options for changing the shape and color for enzymes and metabolites.<br>
          If you want to show RNA expression levels see the expression levels section below.

          <h6 id="">Expression levels</h6>
          To show expression levels, first click the <b>Options</b> button, then click in the "Show expression levels" tick box. This will at the moment, go to HPA and pull in the expression levels for all the proteins in the current graph, and then the drop-down box will be enabled, and here all the HPA tissue RNAseq data is then available. The moment you select one tissue it will color the proteins according to that.

          <div id="" v-html="getExpLvlLegend()"></div><br>

          <h6 id="">Export graph</h6>
          Click the <b>Export graph</b> button, and you will be presented with two options: Graphml or PNG. The first is a Cytoscape compatible GraphML format, including a stylesheet in order to make it identical to the current view.

          <h6 id="">The property of the selected metabolite/enzyme box</h6>
          Depending on whether you have selected (by clicking on the graph) a metabolite or an enzyme different fields will be shown here. But generally this should display the most relevant information for the selected reaction component, such as function, activity, and mass.

          <h6 id="">Metabolite list</h6>
          All the metabolites, eg the nodes, of the above graph are shown in this table, along with some basic information such as name and type. Selecting a row will select it in the graph, and vice versa.

          <h3 id="Map Viewer">Map Viewer</h3>
          <h4 id="2D Viewer">2D Viewer</h4>
          <h4 id="3D Viewer">3D Viewer</h4>
          <h3 id="Global search">Global search</h3>
          If you for instance searched for ATP and then pressed Enter you will see that there are 11 metabolites that match this search term because sATP is found in 8 compartments, and dATP in 3.<br>
          In addition 11 enzymes match ATP, because there are whole families of ATP-related proteins.<br>
          In addition 739 reactions use, or produce ATP.<br>
          Click on the ID in order to be taken to the corresponding page.<br>
          On this page you also have the option of searching, but here it will instead search in the entire data, eg <i>across GEMs</i>.

          <h3 id="API">API</h3>
          Link to the API for the GEM visualisation database part of this website.

          <h3 id="GEMs">GEMs</h3>
          <h4 id="Repository">Repository</h4>
          List all models that the group have made, note that this include both older models that might no longer be maintained (for example HMR have been replaced with HMR2), but also those just published.

          <h4 id="Comparison">Comparison</h4>
          <h4 id="FTP download">FTP download</h4>
          Genome-Scale Metabolic model files can be downloaded from <a href="http://ftp.icsb.chalmers.se">ftp.icsb.chalmers.se</a> or by connecting to the FTP using your favorite FTP client (e.g. <a href="https://filezilla-project.org/">FileZilla</a>).
          <br>
          <span class="has-text-weight-bold lab">Host:</span> <a href="http://ftp.icsb.chalmers.se">ftp.icsb.chalmers.se</a><br>
          <span class="has-text-weight-bold lab">Login:</span> (leave it empty)<br>
          <span class="has-text-weight-bold lab">Password:</span> (leave it empty)<br>
          <span class="has-text-weight-bold lab">Port:</span> 21

          <h3 id="Resources">Resources</h3>
          Some of the most relevant software tools and algorithms that the group have published could be found here, for example STIG-met, Kiwi, and Raven.
          Some of the databases that the group have generated are linked from here, for example Human Cancer Secretome Database (HCSD) and stress response in yeast (yStreX).

          <h3 id="Privacy">Privacy statement</h3>
          The Metabolic Atlas gathers information about users solely to improve the usability and usefulness of the site. There are two types of cookie that are set by the Metabolic Atlas:<br>
          <strong>Functionality cookies</strong> are used to personalize the appearence of the Metabolic Atlas.<br>
          <strong>Tracking cookies</strong> are used via private analytics to track the users on our website. We use them to anonymously observe the behaviour on our website in order to improve it. This information is not shared with any third party.

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

<style lang="scss"></style>
