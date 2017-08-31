<template>
  <div>
    <section class="section">
      <div class="container">
          <h4 class="title is-4">Comparing two models</h4>
          <h6 class="subtitle is-6">{{ comparison.Summary.SharedReactions }} complete shared reactions</h6>
          <table class="table is-narrow is-bordered">
            <thead>
              <tr>
                <th></th>
                <th>Model</td>
                <th>Description</td>
                <th># of reactions</td>
                <th>Shared reactions overlap</td>
                <th>Exclusive reactions</td>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(model, key) in comparison.Models">
                <td>{{ key }}</td>
                <td>{{ model.ModelId }}</td>
                <td>{{ model.ModelName }}</td>
                <td>{{ model.TotalReactions }} reactions</td>
                <td>{{ Math.round(comparison.Summary.SharedReactions / model.TotalReactions * 100) }}%</td>
                <td>{{ key === 'A' ? comparison.Summary.ReactionsOnlyInA : comparison.Summary.ReactionsOnlyInB }} reactions</td>
              </tr>
            </tbody>
          </table>
          In addition another {{ amountRxnDifMod  }} reactions are the same, but different modifiers are 'indicated' in the two models.</br>
      </div>
    </section>
  
    <section class="section">
      <div class="container">
        <h4 class="title is-4">Ranked affected parts</h4>
        <div class="columns">
          <div class="column">
            <h6 class="subtitle is-6">Subsystems by missing reactions</h6>
            <table class="table is-narrow">
              <thead>
                <tr>
                  <th>Subsystem</th>
                  <th>reactions</th>
                  <th><div v-bind:title="comparison.Models.A.ModelId">A</div></th>
                  <th><div v-bind:title="comparison.Models.B.ModelId">B</div></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="subsys in topAffectedSysMis">
                  <td>{{ subsys.name }}</td>
                  <td>{{ subsys.totalMissing }}</td>
                  <td>{{ subsys.MissingReactionsFromA }}</td>
                  <td>{{ subsys.MissingReactionsFromB }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="column">
            <h6 class="subtitle is-6">Subsystems by gene expression</h6>
            <table class="table is-narrow">
              <thead>
                <tr>
                  <th>Subsystem</th>
                  <th>reactions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="subsys in topAffectedSysGenEx">
                  <td>{{ subsys.name }}</td>
                  <td>{{ subsys.DifferentModifiers }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="column">
            <h6 class="subtitle is-6">Compartments by missing reactions</h6>
            <table class="table is-narrow">
              <thead>
                <tr>
                  <th>Compartments</th>
                  <th>reactions</th>
                  <th><div v-bind:title="comparison.Models.A.ModelId">A</div></th>
                  <th><div v-bind:title="comparison.Models.B.ModelId">B</div></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="subsys in topAffectedCompMis">
                  <td>{{ subsys.name }}</td>
                  <td>{{ subsys.totalMissing }}</td>
                  <td>{{ subsys.MissingReactionsFromA }}</td>
                  <td>{{ subsys.MissingReactionsFromB }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <h4 class="title is-4" v-if="showAffected == 'all'">{{ filterableReactions.length }} reactions</h4>
        <h4 class="title is-4" v-if="showAffected == 'lost'">{{ filterableReactions.length }} non-shared (lost) reactions</h4>
        <h4 class="title is-4" v-if="showAffected == 'various'">{{ filterableReactions.length }} shared reactions (VariousModifiers)</h4>
        <h6 class="subtitle is-6">{{ filteredAffectedReactions.length }} filtered, {{ showAffectedReactions.length }} shown</h6>
              <div class="select">
                <select v-model="showAffected" class="select">
                  <option value="all">Show all reactions</option>
                  <option value="lost">Show lost reactions</option>
                  <option value="various">Show various modifiers</option>
                </select>
              </div>
        <table class="table is-narrow">
          <thead>
            <tr>
              <th>
                <input class="input" v-model="filters.modelID" type="text" placeholder="Filter...">
              </th>
              <th>
                <div class="select">
                  <select class="select" v-model="filters.subsystem">
                    <option value="">No filter</option>
                    <option :value="subsys.name" v-for="subsys in allSubsystems">{{ subsys.name }} -- N={{ subsys.nr }}</option>
                  </select>
                </div>
              </th>
              <th>
                <div class="select">
                  <select class="select" v-model="filters.compartment">
                    <option value="">No filter</option>
                    <option :value="comp" v-for="comp in allCompartments">{{ comp }}</option>
                  </select>
                </div>
              </th>
              <th>
                <input class="input" v-if="showAffected !== 'lost'" v-model="filters.filterA" type="text" placeholder="Filter...">
                <div class="select">
                  <select class="select" v-model="filters.tfA" v-if="showAffected !== 'various'">
                    <option value="all">Show all</option>
                    <option :value="true">Only true</option>
                    <option :value="false">Only false</option>
                  </select>
                </div>
              </th>
              <th>
                <input class="input" v-if="showAffected !== 'lost'" v-model="filters.filterB" type="text" placeholder="Filter...">
                <div class="select">
                  <select class="select" v-model="filters.tfB" v-if="showAffected !== 'various'">
                    <option value="all">Show all</option>
                    <option :value="true">Only true</option>
                    <option :value="false">Only false</option>
                  </select>
                </div>
              </th>
              <th><button class="button is-primary" v-on:click="filterAffectedReactions(filters)">Filter</button></th>
            </tr>
            <tr>
              <th>ID</th>
              <th>Subsystem</th>
              <th>Compartment</th>
              <th>A</th>
              <th>B</th>
              <th><button class="button is-primary" v-on:click="drawReactions">Draw</button></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rxn in showAffectedReactions">
              <td><a href="">{{ rxn.ReactionId }}</a></td>
              <td><a href="">{{ rxn.Subsystem }}</a></td>
              <td><a href="">{{ rxn.Compartments.join(', ') }}</a></td>
              <td>
                <template v-if="rxn.ModifierDiferenceses !== null">
                  <a href=""  v-for="mod in rxn.ModifierDiferenceses.ModifiersInANotInB">
                    {{ mod }}
                  </a>
                </template>
                <div v-if="rxn.ModifierDiferenceses === null">{{ rxn.FoundInA }}</div>
              </td>
              <td>
                <template v-if="rxn.ModifierDiferenceses !== null">
                   <a href="" v-for="mod in rxn.ModifierDiferenceses.ModifiersInBNotInA">
                     {{ mod }}
                   </a>
                </template>
                <div v-if="rxn.ModifierDiferenceses === null">{{ rxn.FoundInB }}</div>
              </td>
              <td><input type="checkbox" v-model="reactionsForDraw" v-bind:value="rxn.ReactionId"></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script>
import { default as compareResponse } from '../helpers/compareresp';

export default {
  name: 'compare-models',
  data() {
    return {
      loading: true,
      amountRxnShowing: 3,
      showAffected: 'lost',
      comparison: {},
      filters: {
        modelID: '',
        subsystem: '',
        compartment: '',
        tfA: 'all',
        tfB: 'all',
        filterA: '',
        filterB: '',
      },
      filteredAffectedReactions: [],
      reactionsForDraw: [],
    };
  },
  beforeMount() {
    this.setup();
  },
  mounted() {
    this.filteredAffectedReactions = this.filterableReactions;
  },
  computed: {
    allSubsystems() {
      const all = {};
      for (const rxn of this.filterableReactions) {
        if (!(rxn.Subsystem in all)) {
          all[rxn.Subsystem] = 0;
        }
        all[rxn.Subsystem] += 1;
        // all.add(rxn.Subsystem);
      }
      const subsysList = [];
      for (const subsys of Object.entries(all)) {
        const entry = {};
        entry.name = subsys[0];
        entry.nr = subsys[1];
        subsysList.push(entry);
      }
      function comparer(a, b) {
        return b.nr - a.nr;
      }
      subsysList.sort(comparer);
      return subsysList;
    },
    allCompartments() {
      const all = new Set();
      for (const rxn of this.filterableReactions) {
        for (const comp of rxn.Compartments) {
          all.add(comp);
        }
      }
      return Array.from(all);
    },
    affectedSubsystems() {
      const affectedSubsystems = [];
      for (const subsys of Object.entries(this.comparison.Summary.AffectedSubsystems)) {
        const entry = Object.assign({}, subsys[1]);
        entry.name = subsys[0];
        entry.totalMissing = entry.MissingReactionsFromA + entry.MissingReactionsFromB;
        affectedSubsystems.push(entry);
      }
      return affectedSubsystems;
    },
    affectedCompartments() {
      const affectedCompartments = [];
      for (const comp of Object.entries(this.comparison.Summary.AffectedCompartments)) {
        const entry = Object.assign({}, comp[1]);
        entry.name = comp[0];
        entry.totalMissing = entry.MissingReactionsFromA + entry.MissingReactionsFromB;
        affectedCompartments.push(entry);
      }
      return affectedCompartments;
    },
    filterableReactions() {
      let filterable = [];
      if (this.showAffected === 'lost') {
        filterable = this.comparison.AffectedReactions.LostReactions;
      } else if (this.showAffected === 'various') {
        filterable = this.comparison.AffectedReactions.VariousModifiers;
      } else {
        filterable = this.comparison.AffectedReactions.VariousModifiers.concat(
                     this.comparison.AffectedReactions.LostReactions);
      }
      this.filteredAffectedReactions = filterable;
      return filterable;
    },
    showAffectedReactions() {
      // possibly slice this list if too many
      return this.filteredAffectedReactions.slice(0, 50);
    },
    topAffectedSysMis() {
      function comparer(a, b) {
        return b.totalMissing - a.totalMissing;
      }
      this.affectedSubsystems.sort(comparer);
      return this.affectedSubsystems.slice(0, 5);
    },
    topAffectedSysGenEx() {
      function comparer(a, b) {
        return b.DifferentModifiers - a.DifferentModifiers;
      }
      this.affectedSubsystems.sort(comparer);
      return this.affectedSubsystems.slice(0, 5);
    },
    topAffectedCompMis() {
      function comparer(a, b) {
        return b.totalMissing - a.totalMissing;
      }
      this.affectedCompartments.sort(comparer);
      return this.affectedCompartments.slice(0, 5);
    },
    amountRxnDifMod() {
      return this.comparison.AffectedReactions.VariousModifiers.length;
    },
  },
  methods: {
    setup() {
      // FIXME now loads a JSON file
      this.comparison = JSON.parse(compareResponse());
    },
    filterAffectedReactions(filters) {
      const filteredReactions = [];
      for (const rxn of this.filterableReactions) {
        let show = true;
        if (show && filters.tfA !== 'all' && rxn.ModifierDiferenceses === null &&
            rxn.FoundInA !== filters.tfA) {
          show = false;
        }
        if (show && filters.tfB !== 'all' && rxn.ModifierDiferenceses === null &&
            rxn.FoundInB !== filters.tfB) {
          show = false;
        }
        if (show && filters.filterA &&
            rxn.ModifierDiferenceses !== null &&
            rxn.ModifierDiferenceses.ModifiersInANotInB.join().indexOf(filters.filterA) === -1) {
          show = false;
        }
        if (show && filters.filterB &&
            rxn.ModifierDiferenceses !== null &&
            rxn.ModifierDiferenceses.ModifiersInBNotInA.join().indexOf(filters.filterB) === -1) {
          show = false;
        }
        if (show && filters.modelID !== '' && rxn.ReactionId.indexOf(filters.modelID) === -1) {
          show = false;
        }
        if (show && filters.compartment !== '' &&
            rxn.Compartments.indexOf(filters.compartment) === -1) {
          show = false;
        }
        if (show && filters.subsystem !== '' && rxn.Subsystem !== filters.subsystem) {
          show = false;
        }
        if (show) {
          filteredReactions.push(rxn);
        }
      }
      this.filteredAffectedReactions = filteredReactions;
    },
    drawReactions() {
      console.log(this.reactionsForDraw);
    },
  },
};
</script>

<style lang="scss">

.text {
  padding-left: 0.75em;
}

</style>
