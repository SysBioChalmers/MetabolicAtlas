<template>
  <div class="reactome column" v-show="showTable">
    <h4 class="title is-4">Reactions</h4>
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
      :reactions="reactions" :selectedElmId="ID" :showSubsystem="true" :model="model" :limit="200"></reaction-table>
      <reaction-table v-show="!showLoader && expandAllCompartment"
      :reactions="reactionsAllcompartment" :selectedElmId="ID" :showSubsystem="true" :model="model" :limit="200"></reaction-table>
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
import Loader from 'components/Loader';
import ReactionTable from 'components/explorer/gemBrowser/ReactionTable';

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
      reactomeID: '',
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
    loadReactions(ID) {
      if (this.reactomeID &&
          ((this.expandAllCompartment && this.reactionsAllcompartment.length !== 0) ||
         (!this.expandAllCompartment && this.reactions.length !== 0))) {
        this.reactomeID = ID;
        return;
      }
      this.showLoader = true;
      this.reactomeID = ID;
      let url = `${this.model.database_name}/metabolite/${ID}/reactions/`;
      if (this.expandAllCompartment) {
        url = `${this.model.database_name}/metabolite/${ID}/reactions/all_compartment/`;
      }
      axios.get(url)
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
        .catch(() => {
          this.showLoader = false;
          this.showTable = false;
        });
    },
    toggleExpandAllCompartment() {
      this.expandAllCompartment = !this.expandAllCompartment;
      this.loadReactions(this.ID);
    },
  },
};

</script>

<style lang="scss">

</style>
