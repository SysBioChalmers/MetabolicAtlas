<template>
  <section class="section section-no-top extended-section">
    <div class="container is-fullhd">
      <h3 class="title is-size-3">GEM Comparison</h3>
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

export default {
  name: 'CompareModels',
  data() {
    return {
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
};
</script>

<style lang="scss"></style>
