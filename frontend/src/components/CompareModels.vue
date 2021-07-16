<template>
  <section class="section extended-section">
    <div class="container is-fullhd">
      <h3 class="title is-size-3">GEM Comparison</h3>
      <h6 class="subtitle is-size-6">
        See the common Reactions and Metabolites between 2 or 3 GEMs, or
        <router-link :to="{ name: 'documentation', hash: '#Comparison'}">
          read more about how this comparison
        </router-link>
        is made.
      </h6>
      <div class="comparison-container">
        <div class="comparison-container__picker">
          <div class="tags">
            <span v-for="m in modelList" :key="m.apiName" class="tag is-medium">
              <label class="checkbox" :disabled="shouldDisable(m)">
                <input :id="m.apiName" v-model="selectedModels" :value="m" type="checkbox" :disabled="shouldDisable(m)">
                {{ m.short_name }}
              </label>
            </span>
          </div>
          <template v-if="validModels">
            <loader v-if="comparisonsEmpty" />
            <div v-else>
              <comparison-matrix />
            </div>
          </template>
        </div>
        <comparison-details v-if="validModels && !comparisonsEmpty" />
      </div>
      <br><br>
      <div v-for="(c, id) in comparison" :key="id">
        <h4 class="title is-size-4">{{ c.models.A.modelId }} vs. {{ c.models.B.modelId }}</h4>
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
              <tr v-for="m in c.models" :key="m.modelName">
                <td>{{ m.modelId }}</td>
                <td v-html="m.modelName"></td>
                <td>{{ m.totalReactions }}</td>
                <td>{{ m.sharedReactions }}%</td>
                <td>{{ m.exclusiveReactions }}</td>
                <td>{{ m.exclusivePercentage }}</td>
              </tr>
            </tbody>
          </table>
        </div>
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
        <br><br>
      </div>
    </div>
  </section>

</template>

<script>

import { mapGetters, mapState } from 'vuex';
import ComparisonMatrix from '@/components/shared/ComparisonMatrix.vue';
import ComparisonDetails from '@/components/shared/ComparisonDetails.vue';
import Loader from '@/components/Loader.vue';

export default {
  name: 'CompareModels',
  components: {
    ComparisonMatrix,
    ComparisonDetails,
    Loader,
  },
  data() {
    return {
      comparing: false,
      minModels: 2,
      maxModels: 3,
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
    }),
    ...mapGetters({
      comparisonsEmpty: 'compare/comparisonsEmpty',
    }),
    validModels() {
      return this.selectedModels.length >= this.minModels && this.selectedModels.length <= this.maxModels;
    },
  },
  watch: {
    modelList() {
      this.restoreFromQuery();
    },
    async selectedModels(models) {
      if (!models) {
        return;
      }

      const query = {
        models: models.map(m => `${m.apiName}-${m.version}`),
      };

      if (JSON.stringify(query.models) !== JSON.stringify([this.$route.query.models].flat())) {
        this.$router.replace({ query });
      }

      await this.compare();
    },
  },
  mounted() {
    this.restoreFromQuery();
  },
  methods: {
    selectedModelIndex(model) {
      return this.selectedModels.findIndex(m => model.apiName === m.apiName
        && model.version === m.version);
    },
    shouldDisable(model) {
      return this.selectedModelIndex(model) === -1 && this.selectedModels.length === this.maxModels;
    },
    async compare() {
      if (!this.validModels || this.comparing) {
        return;
      }

      this.comparing = true;
      this.$store.dispatch('compare/resetComparisons');

      const payload = {
        models: this.selectedModels.map(m => ({
          model: m.apiName,
          version: m.apiVersion,
        })),
      };
      await this.$store.dispatch('compare/getComparisons', payload);
      this.comparing = false;
    },
    restoreFromQuery() {
      if (this.modelList.length === 0) {
        return;
      }

      const { models } = this.$route.query;

      if (models) {
        const mappedModels = [models].flat().map((m) => {
          const [apiName, version] = m.split('-');
          return this.modelList.find(x => x.apiName === apiName && x.version === version);
        });
        const matchingModels = mappedModels.filter(m => m);
        const uniqueMatchingModels = new Set(matchingModels);

        this.selectedModels = [...uniqueMatchingModels].splice(0, this.maxModels);
      } else {
        const [m1, m2] = this.modelList;
        this.selectedModels = [m1, m2];
      }
    },
  },
};
</script>

<style lang="scss" scoped>

.control[disabled] {
  cursor: not-allowed;
  pointer-events: none;
  user-select: none;
}

.comparison-container {
  display: flex;
  flex-direction: column;

  &__picker {
    margin-bottom: 2em;
    margin-right: 0;
  }
}

@media (min-width: $tablet) {
  .comparison-container {
    flex-direction: row;

    &__picker {
      display: block;
      margin-bottom: 0;
      margin-right: 2em;
    }
  }
}

</style>
