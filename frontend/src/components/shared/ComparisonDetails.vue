<template>
  <div class="card">
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
          <p v-if="selectedCell.position.row !== selectedCell.position.col">
            Compared to {{ comparedModels }}, it has
            {{ comparisonDetails.details['Reaction'].common }} reactions and
            {{ comparisonDetails.details['CompartmentalizedMetabolite'].common }} metabolites in common.
          </p>
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
    }),
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
