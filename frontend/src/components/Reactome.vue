<template>
  <div class="reactome column">
    <h3 class="title is-3">Reactome</h3>
    <div class="container">
      <div v-show="false" id="diagram"></div>
      <p class="control field">
        <button class="button"
        @click="toggleExpandAllCompartment">
          <span v-show="!expandAllCompartment">Expand to all compartments</span>
          <span v-show="expandAllCompartment">Restrict to current compartment</span>
          </button>
      </p>
      <reaction-table v-show="!showLoader && !expandAllCompartment" :reactions="reactions" :selectedElmId="elementID" :showSubsystem="true"></reaction-table>
      <reaction-table v-show="!showLoader && expandAllCompartment" :reactions="reactionsAllcompartment" :selectedElmId="elementID" :showSubsystem="true"></reaction-table>
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
  props: ['model'],
  data() {
    return {
      errorMessage: '',
      reactions: [],
      reactionsAllcompartment: [],
      reactome: null,
      showLoader: true,
      expandAllCompartment: false,
      elementID: '',
    };
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      this.loadReactions();
    },
  },
  mounted() {
    this.loadReactions();
    // this.drawDiagram();
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
    loadReactions() {
      let ID = this.$route.params.id || this.$route.query.id;
      if (this.elementID === ID &&
         ((this.expandAllCompartment && this.reactionsAllcompartment.length !== 0) ||
         (!this.expandAllCompartment && this.reactions.length !== 0))) {
        return;
      }
      this.showLoader = true;
      this.elementID = ID;
      if (this.expandAllCompartment) {
        ID = ID.replace(/[a-z]$/, '');
      }
      axios.get(`${this.model}/metabolites/${ID}/reactions/`)
        .then((response) => {
          this.errorMessage = '';
          if (this.expandAllCompartment) {
            this.reactionsAllcompartment = response.data;
          } else {
            this.reactions = response.data;
          }
          this.showLoader = false;
        })
        .catch((error) => {
          this.loading = false;
          switch (error.response.status) {
            case 404:
              this.errorMessage = this.$t('notFoundError');
              break;
            default:
              this.errorMessage = this.$t('unknownError');
          }
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
      this.loadReactions();
    },
  },
};

</script>

<style lang="scss">

</style>
