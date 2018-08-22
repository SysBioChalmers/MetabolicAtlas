<template>
  <div class="reactome column" v-show="showTable">
    <h4 class="title is-4">Reactome</h4>
    <div class="container">
      <div v-show="false" id="diagram"></div>
      <p class="control field">
        <button class="button"
        @click="toggleExpandAllCompartment">
          <span v-show="!expandAllCompartment">Expand to all compartments</span>
          <span v-show="expandAllCompartment">Restrict to current compartment</span>
          </button>
      </p>
      <reaction-table v-show="!showLoader && !expandAllCompartment" 
      :reactions="reactions" :selectedElmId="ID" :showSubsystem="true"></reaction-table>
      <reaction-table v-show="!showLoader && expandAllCompartment" 
      :reactions="reactionsAllcompartment" :selectedElmId="ID" :showSubsystem="true"></reaction-table>
      <div v-if="errorMessage" class="columns">
        <div class="column notification is-danger is-half is-offset-one-quarter has-text-centered">
          {{ errorMessage }}
        </div>
      </div>
      <div v-show="!errorMessage">
        <loader v-show="showLoader"></loader>
      </div>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import SVG from 'svg.js';
import 'svg.connectable.js';
import 'svg.draggy.js';
import Loader from 'components/Loader';
import ReactionTable from 'components/ReactionTable';

export default {
  name: 'reactome',
  components: {
    ReactionTable,
    Loader,
  },
  props: ['model', 'metaboliteID'],
  data() {
    return {
      errorMessage: '',
      reactions: [],
      reactionsAllcompartment: [],
      reactome: null,
      showLoader: true,
      showTable: false,
      expandAllCompartment: false,
      ID: '',
      reactomeID: '', // might be without compartment letters
    };
  },
  watch: {
    metaboliteID() {
      if (this.metaboliteID) {
        this.ID = this.metaboliteID;
        this.reactomeID = '';
        this.reactions = [];
        this.reactionsAllcompartment = [];
        this.expandAllCompartment = false;
        this.loadReactions(this.ID);
      }
    },
  },
  methods: {
    drawDiagram() {
      /*
        TODO: the following is a start into laying out a reactome diagram
        A small tool needs to be developed in order to generate the diagram.
      */
      const diagram = new SVG('diagram').size('100%', 500);

      const links = diagram.group();
      const markers = diagram.group();
      const nodes = diagram.group();

      const g1 = nodes.group().translate(100, 200).draggy();
      g1.ellipse(100, 50).fill('#C2185B');

      const g2 = nodes.group().translate(300, 200).draggy();
      g2.ellipse(100, 50).fill('#E91E63');

      const g3 = nodes.group().translate(600, 200).draggy();
      g3.ellipse(100, 50).fill('#FF5252');
      g3.plain('R.HMR.5816').attr({ x: -150, y: 10 });

      g1.connectable({
        container: links,
        markers,
      }, g2).setLineColor('#5D4037');

      g2.connectable({
        padEllipse: true,
      }, g3).setLineColor('#5D4037');
    },
    loadReactions(ID) {
      if (this.reactomeID &&
          (ID !== this.reactomeID) &&
          ((this.expandAllCompartment && this.reactionsAllcompartment.length !== 0) ||
         (!this.expandAllCompartment && this.reactions.length !== 0))) {
        this.reactomeID = ID;
        return;
      }
      this.showLoader = true;
      this.reactomeID = ID;
      axios.get(`${this.model}/metabolites/${ID}/reactions/`)
        .then((response) => {
          this.errorMessage = '';
          if (this.expandAllCompartment) {
            this.reactionsAllcompartment = response.data;
          } else {
            this.reactions = response.data;
          }
          this.showTable = true;
          this.showLoader = false;
        })
        .catch((error) => {
          console.log(error);
          this.showLoader = false;
          this.showTable = false;
        });
    },
    // TODO: call loadReactome when selecting a row from the table of reactions
    loadReactome(reactionId) {
      const rcid = this.$route.params.id || this.$route.query.id;
      axios.get(`metabolite_reactions/${rcid}/reactome/${reactionId}`)
        .then((response) => {
          this.errorMessage = '';
          this.reactome = response.data;
          this.showLoader = false;
        });
    },
    toggleExpandAllCompartment() {
      this.expandAllCompartment = !this.expandAllCompartment;
      if (this.expandAllCompartment) {
        this.loadReactions(this.ID.replace(/[a-z]{1,3}$/, ''));
      } else {
        this.loadReactions(this.ID);
      }
    },
  },
};

</script>

<style lang="scss">

</style>
