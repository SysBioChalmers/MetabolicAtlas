<template>
  <div>
    <div class="container">
        <h2>Comparing two models</h2>
        <table class="table is-narrow is-bordered">
          <tbody>
            <tr v-for="model in comparison.Models">
              <td>{{ model.ModelId }}</td>
              <td>{{ model.ModelName }}</td>
              <td>{{ model.TotalReactions }} reactions</td>
              
            </tr>
          </tbody>
        </table>
      </br>
        <h2>Differences found:</h2>
        {{ comparison.Summary.SharedReactions }} complete shared reactions [{{ Math.round(comparison.Summary.SharedReactions / comparison.Models.A.TotalReactions * 100) }}% shared of As reaction set] [{{ Math.round(comparison.Summary.SharedReactions / comparison.Models.B.TotalReactions * 100) }}% shared of Bs reaction set]</br>
        {{ comparison.Summary.ReactionsOnlyInA }} reactions only in A and {{ comparison.Summary.ReactionsOnlyInB }} reactions only in B</br>

        <font color='orange'>FIXME where does this 611 come from?</font>
        In addition another 611 reactions are the same, but different modifiers are 'indicated' in the two models.</br>
      </br>

<div class="columns">
  <div class="column">
    <table class="table is-narrow">
      <thead>
        <tr><th colspan="4">Most affected subsystems by missing reactions</th></tr>
        <tr>
          <th>Subsystem</th>
          <th>reactions</th>
          <th>A</th>
          <th>B</th>
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
    <table class="table is-narrow">
      <thead>
        <tr><th colspan="2">Most affected subsystems by gene expression</th></tr>
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
    <table class="table is-narrow">
      <thead>
        <tr><th colspan="4">Most affected compartments by missing reactions</th></tr>
        <tr>
          <th>Subsystem</th>
          <th>reactions</th>
          <th>A</th>
          <th>B</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="subsys in topAffectedCompMis">
          <td>{{ subsys.name }}></td>
          <td>{{ subsys.totalMissing }}</td>
          <td>{{ subsys.MissingReactionsFromA }}</td>
          <td>{{ subsys.MissingReactionsFromB }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
<font color="orange">See more needs implementing and 
Each of the names should be a link -> show on the SVG</font>
</br>
</br>
      <font color='orange'>The below table should show all (?) affected reactions,
      so it has to be possible to filter the table!</font>
    <table class="table is-narrow">
      <thead>
        <tr><th colspan="6">All {{ amountReactions }} affected reactions</th></tr>
        <tr>
          <th>ID</th>
          <th>Subsystem</th>
          <th>Compartment</th>
          <th>A</th>
          <th>B</th>
          <th>Show on map</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="rxn in comparison.AffectedReactions.VariousModifiers">
          <td><a href="show on map">{{ rxn.ReactionId }}</a></td>
          <td>{{ rxn.Subsystem }}</td>
          <td>{{ rxn.Compartments.join(', ') }}</td>
          <td>
            <a href="" v-for="mod in rxn.ModifierDiferenceses.ModifiersInANotInB">
              {{ mod }}
            </a>
          </td>
          <td>
            <a href="" v-for="mod in rxn.ModifierDiferenceses.ModifiersInBNotInA">
              {{ mod }}
            </a>
          </td>
        </tr>
      </tbody>
    </table>
<!--
        <h2>The 3355 affected Reactions:</h2>
        <table>
          <tr><th>ReactionID</th><th>Subsystem</th><th>Compartment</th><th>A</th><th>B</th><th>Show on map</td></tr>
          <tr><td>R_HMR_3905</td><td>Glycolysis / Gluconeogenesis</td><td>Cytosol</td>
            <td><a href="">E_1357</a>, <a href="">E_1981</a>, <a href="">E_2141</a></td>
            <td><a href="">E_1340</a>, <a href="">E_1871</a>, <a href="">E_1978</a>,
              <a href="">E_2090</a>, <a href="">E_2109</a>, <a href="">E_2119</a>,
              <a href="">E_2151</a>, <a href="">E_2158</a>, <a href="">E_2309</a></td>
            <td><input type="radio"></tr>
          <tr><td>R_HMR_8585</td><td>Starch and sucrose metabolism</td><td>Cytosol</td><td>Yes</td><td>No</td></tr>
          <tr><td>R_HMR_8570</td><td>Starch and sucrose metabolism</td><td>Cytosol</td><td>No</td><td>Yes</td></tr>
</tbody>
        </table>
        <font color='orange'>Clicking on the radio button should instantly load the corresponding.... WHAT NEEDS LOADING AND WHY A RADIO BUTTON AND NOT A LINK?</font>
      </br>
      <font color='orange'>Do we want to do some sort of GO overrepresentation analysis of the
        enzymes that are found in A but not B (and vice verse)?</font>
-->
    </div>
  </div>
</template>

<script>
import { default as compareResponse } from '../helpers/compareresp';

export default {
  name: 'compare-models',
  data() {
    return {
      loading: true,
      comparison: {},
    };
  },
  beforeMount() {
    this.setup();
  },
  computed: {
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
    amountReactions() {
      return (this.comparison.AffectedReactions.VariousModifiers.length +
              this.comparison.AffectedReactions.LostReactions.length);
    },
  },
  methods: {
    setup() {
      // FIXME now loads a JSON file
      this.comparison = JSON.parse(compareResponse());
    },
  },
};
</script>

<style lang="scss">

.text {
  padding-left: 0.75em;
}

</style>
