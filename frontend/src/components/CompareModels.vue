<template>
  <section class="section section-no-top extended-section">
    <div class="container is-fullhd">
      <h3 class="title is-size-3">GEM Comparison</h3>
      <div class="columns">
        <div class="column is-one-third">
          <h5 class="subtitle is-size-5">Component:</h5>
          <div class="control">
            <label class="radio" @click="setComponentType('Reaction')">
              <input v-model="componentType" name="componentType" type="radio" value="Reaction">
              Reaction
            </label>
          </div>
          <div class="control">
            <label class="radio" @click="setComponentType('CompartmentalizedMetabolite')">
              <input v-model="componentType" name="componentType" type="radio" value="CompartmentalizedMetabolite">
              Metabolite
            </label>
          </div>
          <h5 class="subtitle is-size-5">Models:</h5>
          <div v-for="model in modelList" :key="model.apiName" class="control"
               @click="toggleSelectedModel(model)">
            <label class="checkbox" :disabled="shouldDisable(model)">
              <input :checked="selectedModelIndex(model) > -1" type="checkbox">
              {{ model.apiName }}
            </label>
          </div>
          <br />
          <div class="buttons">
            <button class="button is-primary" :disabled="selectedModels.length < 2" @click="compare">Compare</button>
          </div>
        </div>
        <div v-if="comparisons.length > 0" class="column">
          Table
          <table class="table is-striped">
            <thead>
              <tr>
                <th>have in common with ↓</th>
                <th v-for="model in selectedModels" :key="model.apiName">
                  {{ model.apiName }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(heading, i) in rowHeadings" :key="heading + i">
                <th>{{ heading }}</th>
                <td v-for="(m, j) in selectedModels" :key="heading + j">
                  {{ comparisonRows[i][j] }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <template v-for="c in comparison">
        <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
        <br>
        <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
        <h4 class="title is-size-4">{{ c.models.A.modelId }} vs. {{ c.models.B.modelId }}</h4>
        <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
        <div class="table-container">
          <table class="is-fullwidth table is-narrow">
            <thead>
              <tr>
                <th>Model</th>
                <th>Description</th>
                <th>Reactions</th>
                <th>Shared reactions</th>
                <th>Exclusive reactions</th>
                <th>Exclusive reactions %</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="model in c.models" :key="model.modeName">
                <td>{{ model.modelId }}</td>
                <td v-html="model.modelName"></td>
                <td>{{ model.totalReactions }}</td>
                <td>{{ model.sharedReactions }}%</td>
                <td>{{ model.exclusiveReactions }}</td>
                <td>{{ model.exclusivePercentage }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
        <div class="columns is-variable is-8">
          <div class="column">
            <h5 class="subtitle is-size-5">Exclusive reactions by compartment</h5>
            <div class="table-container">
              <table class="table is-fullwidth is-striped is-hoverable">
                <thead>
                  <tr>
                    <th>Compartment</th>
                    <th>Human-GEM total</th>
                    <th>{{ c.models.A.modelId }}-exclusive</th>
                    <th>{{ c.models.B.modelId }}-exclusive</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="subsys in c.compartments" :key="subsys.name">
                    <td>{{ subsys.name }}</td>
                    <td>{{ subsys.totalMissing }}</td>
                    <td>{{ subsys.missingReactionsFromA }}</td>
                    <td>{{ subsys.missingReactionsFromB }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p>Note: some reactions are associated with multiple compartments.</p>
          </div>

          <div class="column">
            <h5 class="subtitle is-size-5">Exclusive reactions by subsystem</h5>
            <div class="table-container">
              <table class="table is-fullwidth is-striped is-hoverable">
                <thead>
                  <tr>
                    <th>Subsystem</th>
                    <th>Human-GEM total</th>
                    <th>{{ c.models.A.modelId }}-exclusive</th>
                    <th>{{ c.models.B.modelId }}-exclusive</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="subsys in c.subsystems" :key="subsys.name">
                    <td>{{ subsys.name }}</td>
                    <td>{{ subsys.totalMissing }}</td>
                    <td>{{ subsys.missingReactionsFromA }}</td>
                    <td>{{ subsys.missingReactionsFromB }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
        <br><br>
      </template>
    </div>
  </section>

</template>

<script>

import { mapState } from 'vuex';

export default {
  name: 'CompareModels',
  data() {
    return {
      componentType: 'Reaction',
      selectedModels: [],
      comparison: [{
        models: {
          A: {
            modelId: 'Human-GEM v1.0.2',
            modelName: 'The generic genome-scale metabolic model of <i>Homo sapiens</i> integrated from HMR2 and Recon3D',
            totalReactions: 13520,
            sharedReactions: 60.45,
            exclusiveReactions: 5346,
            exclusivePercentage: 39.54,
          },
          B: {
            modelId: 'HMR2',
            modelName: 'Genome-scale metabolic model for the generic human cell',
            totalReactions: 8181,
            sharedReactions: 99.91,
            exclusiveReactions: 7,
            exclusivePercentage: 0.08,
          },
        },
        subsystems: [
          { name: 'Transport reactions',
            totalMissing: '4247',
            missingReactionsFromA: '1644',
            missingReactionsFromB: '0',
          },
          { name: 'Exchange/demand reactions',
            totalMissing: '1665',
            missingReactionsFromA: '1210',
            missingReactionsFromB: '7',
          },
          { name: 'Drug metabolism',
            totalMissing: '573',
            missingReactionsFromA: '573',
            missingReactionsFromB: '-',
          },
          { name: 'Fatty acid oxidation',
            totalMissing: '542',
            missingReactionsFromA: '542',
            missingReactionsFromB: '-',
          },
          { name: 'Peptide metabolism',
            totalMissing: '242',
            missingReactionsFromA: '242',
            missingReactionsFromB: '-',
          },
        ],
        compartments: [
          { name: 'Cytosol',
            totalMissing: '8322',
            missingReactionsFromA: '2990',
            missingReactionsFromB: '0',
          },
          { name: 'Extracellular',
            totalMissing: '5131',
            missingReactionsFromA: '2934',
            missingReactionsFromB: '7',
          },
          { name: 'Boundary',
            totalMissing: '1666',
            missingReactionsFromA: '1207',
            missingReactionsFromB: '7',
          },
          { name: 'Endoplasmic reticulum',
            totalMissing: '1400',
            missingReactionsFromA: '604',
            missingReactionsFromB: '0',
          },
          { name: 'Mitochondria',
            totalMissing: '1633',
            missingReactionsFromA: '516',
            missingReactionsFromB: '0',
          },
        ],
      },
      {
        models: {
          A: {
            modelId: 'Human-GEM v1.0.2',
            modelName: 'The generic genome-scale metabolic model of <i>Homo sapiens</i> integrated from HMR2 and Recon3D',
            totalReactions: 13520,
            sharedReactions: 96.85,
            exclusiveReactions: 425,
            exclusivePercentage: 3.14,
          },
          B: {
            modelId: 'Recon3D',
            modelName: 'Human metabolic network reconstruction integrating pharmacogenomic associations, large-scale phenotypic data, and structural information for proteins and metabolites',
            totalReactions: 13543,
            sharedReactions: 98.09,
            exclusiveReactions: 258,
            exclusivePercentage: 1.9,
          },
        },
        subsystems: [
          { name: 'Transport reactions',
            totalMissing: '4247',
            missingReactionsFromA: '208',
            missingReactionsFromB: '0',
          },
          { name: 'Exchange/demand reactions',
            totalMissing: '1665',
            missingReactionsFromA: '24',
            missingReactionsFromB: '250',
          },
          { name: 'N-glycan metabolism',
            totalMissing: '151',
            missingReactionsFromA: '20',
            missingReactionsFromB: '0',
          },
          { name: 'Bile acid biosynthesis',
            totalMissing: '243',
            missingReactionsFromA: '12',
            missingReactionsFromB: '0',
          },
          { name: 'Bile acid recycling',
            totalMissing: '33',
            missingReactionsFromA: '10',
            missingReactionsFromB: '-',
          },
        ],
        compartments: [
          { name: 'Cytosol',
            totalMissing: '8322',
            missingReactionsFromA: '312',
            missingReactionsFromB: '194',
          },
          { name: 'Extracellular',
            totalMissing: '5131',
            missingReactionsFromA: '177',
            missingReactionsFromB: '1',
          },
          { name: 'Mitochondria',
            totalMissing: '1633',
            missingReactionsFromA: '59',
            missingReactionsFromB: '11',
          },
          { name: 'Endoplasmic reticulum',
            totalMissing: '1400',
            missingReactionsFromA: '32',
            missingReactionsFromB: '14',
          },
          { name: 'Golgi apparatus',
            totalMissing: '454',
            missingReactionsFromA: '22',
            missingReactionsFromB: '11',
          },
        ],
      }],
    };
  },
  computed: {
    ...mapState({
      modelList: state => state.models.modelList,
      comparisons: state => state.compare.comparisons,
      maxModels() {
        return this.componentType === 'Reaction' ? 4 : 3;
      },
      rowHeadings() {
        if (this.selectedModels.length < 2) {
          return [];
        }

        let headings = this.selectedModels.map(m => m.apiName);

        if (this.selectedModels.length === 4) {
          const [h1, h2, h3, h4] = headings;

          headings = [
            ...headings,
            `${h1} + ${h2}`,
            `${h1} + ${h3}`,
            `${h1} + ${h4}`,
            `${h2} + ${h3}`,
            `${h2} + ${h4}`,
            `${h3} + ${h4}`,
          ];
        }

        if (this.selectedModels.length > 2) {
          headings.push('all others');
        }

        return headings;
      },
      comparisonRows() {
        const singles = this.comparisons.filter(c => Object.keys(c).length === 1);
        const doubles = this.comparisons.filter(c => Object.keys(c).length === 2);
        const triples = this.comparisons.filter(c => Object.keys(c).length === 3);
        const quadruples = this.comparisons.filter(c => Object.keys(c).length === 4);

        return this.rowHeadings.map((h, i) => this.selectedModels.map((m, j) => {
          let comparison;

          if (m.apiName === h) {
            comparison = singles.find(x => Object.keys(x)[0] === m.apiName);
          } else if (i < this.selectedModels.length && j < this.selectedModels.length) {
            comparison = doubles.find(x => Object.keys(x).includes(h) && Object.keys(x).includes(m.apiName));
          } else if (i === this.rowHeadings.length - 1) { // if last row
            comparison = this.selectedModels.length === 3 ? triples[0] : quadruples[0];
          } else {
            const [k1, k2] = h.split(' + '); // e.g. HumanGem + MouseGem
            comparison = k1 !== m.apiName && k2 !== m.apiName && triples.find(x => Object.keys(x).includes(k1)
              && Object.keys(x).includes(k2) && Object.keys(x).includes(m.apiName));
          }

          return comparison ? comparison[m.apiName] : '-';
        }));
      },
    }),
  },
  methods: {
    setComponentType(componentType) {
      if (this.componentType === componentType) {
        return;
      }

      this.$store.dispatch('compare/resetComparisons');
      this.componentType = componentType;

      if (this.selectedModels.length > this.maxModels) {
        this.selectedModels.splice(this.maxModels, this.selectedModels.length - this.maxModels);
      }
    },
    selectedModelIndex(model) {
      return this.selectedModels.findIndex(m => model.apiName === m.apiName
        && model.version === m.version);
    },
    toggleSelectedModel(model) {
      this.$store.dispatch('compare/resetComparisons');

      const index = this.selectedModelIndex(model);

      if (index > -1) {
        this.selectedModels.splice(index, 1);
      } else {
        this.selectedModels.push(model);
      }
    },
    shouldDisable(model) {
      return this.selectedModelIndex(model) === -1 && this.selectedModels.length === this.maxModels;
    },
    async compare() {
      this.$store.dispatch('compare/resetComparisons');

      const payload = {
        type: this.componentType,
        models: this.selectedModels.map(m => ({
          model: m.apiName,
          version: m.apiVersion,
        })),
      };
      await this.$store.dispatch('compare/getComparisons', payload);
    },
  },
};
</script>

<style lang="scss"></style>
