<template>
  <div id="comparison-details" class="card">
    <template v-if="comparisonDetails">
      <header class="card-header">
        <p class="card-header-title">
          {{ comparisonDetails.models.model.model }}
        </p>
      </header>
      <div class="card-content">
        <div class="content">
          <p>
            The {{ comparisonDetails.models.model.model }} has
            {{ comparisonDetails.details['Reaction'].own }} reactions and
            {{ comparisonDetails.details['CompartmentalizedMetabolite'].own }} metabolites.
          </p>
          <div v-if="selectedCell.position.row !== selectedCell.position.col">
            Compared to {{ comparedModels }}, it has:
            <ul>
              <li>
                {{ comparisonDetails.details['Reaction'].common }} reactions and
                {{ comparisonDetails.details['CompartmentalizedMetabolite'].common }} metabolites in common
              </li>
              <li>
                {{ comparisonDetails.details['Reaction'].unique.length }} unique reactions
                <br />
                <div class="tags">
                  <span v-for="id in comparisonDetails.details['Reaction'].unique"
                        :key="id" class="tags">
                    <router-link :to="{ name: 'reaction', params: { model: currentModel.short_name, id } }">
                      {{ id }}
                    </router-link>
                  </span>
                </div>
              </li>
              <li>
                {{ comparisonDetails.details['CompartmentalizedMetabolite'].unique.length }} unique metabolites
                <br />
                <div class="tags">
                  <span v-for="id in comparisonDetails.details['CompartmentalizedMetabolite'].unique"
                        :key="id" class="tags">
                    <router-link :to="{ name: 'metabolite', params: { model: currentModel.short_name, id } }">
                      {{ id }}
                    </router-link>
                  </span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </template>
    <div v-else class="content">
      <loader />
    </div>
  </div>
</template>

<script>

import { mapState } from 'vuex';
import Loader from '@/components/Loader.vue';

export default {
  name: 'ComparisonDetails',
  components: {
    Loader,
  },
  data() {
    return {
    };
  },
  computed: {
    ...mapState({
      selectedCell: state => state.compare.selectedCell,
      comparisonDetails: state => state.compare.comparisonDetails,
      modelList: state => state.models.modelList,
    }),
    currentModel() {
      if (!this.comparisonDetails || this.modelList.length === 0) {
        return null;
      }

      return this.modelList.find(m => m.apiName === this.comparisonDetails.models.model.model);
    },
    comparedModels() {
      if (!this.comparisonDetails) {
        return [];
      }
      return this.comparisonDetails.models.models.map(m => m.model).join(' and ');
    },
  },
  watch: {
    async selectedCell(cell) {
      if (!cell) return;

      const { model, models } = cell;
      await this.$store.dispatch('compare/getComparisonDetails', { model, models });
    },
  },
  methods: {
  },
};

</script>

<style lang="scss" scoped>
  .card {
    padding: 0;
  }
</style>
