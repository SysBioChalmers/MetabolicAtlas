<template>
  <section class="section extended-section">
    <div>
      <div class="container">
          <h3 class="title is-size-3">Comparing two models</h3>
          <h6 class="subtitle is-6">{{ comparison.Summary.SharedReactions }} complete shared reactions</h6>
          <table class="table is-narrow is-bordered">
            <thead>
              <tr>
                <th></th>
                <th>Model</th>
                <th>Description</th>
                <th># of reactions</th>
                <th>Shared reactions overlap</th>
                <th>Exclusive reactions</th>
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
          In addition another 4619 reactions are the same, but different modifiers are 'indicated' in the two models.</br>
      </div>
    </div>
    <br><br>
    <div>
      <div class="container">
        <h3 class="title is-size-3">Ranked affected parts</h3>
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
    </div>
  </section>

</template>

<script>
import { default as compareResponse } from '../helpers/compareresp';

export default {
  name: 'compare-models',
  data() {
    return {
      comparison: {},
    };
  },
  beforeMount() {
    this.setup();
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
  },
  methods: {
    setup() {
      this.comparison = JSON.parse(compareResponse());
    },
  },
};
</script>

<style lang="scss"></style>
