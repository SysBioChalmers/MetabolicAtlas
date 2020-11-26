<template>
  <div id="comparison-details" class="card">
    <header class="card-header">
      <p class="card-header-title">
        Comparison Details&nbsp;
        <span v-if="comparisonDetails">
          | {{ currentModel.short_name }} ⇄ {{ comparedModels }}
        </span>
      </p>
    </header>
    <div class="card-content">
      <div v-if="comparisonDetails" class="content">
        <p>
          The <b>{{ currentModel.short_name }}</b> has
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
            <li v-for="t in Object.keys(types)" :key="t">
              {{ comparisonDetails.details[types[t]].unique.length }} unique {{ t }}s
              <span v-if="comparisonDetails.details[types[t]].unique.length > 20">
                (showing 20)
              </span>
              <br />
              <div class="tags">
                <span v-for="id in comparisonDetails.details[types[t]].unique.slice(0,20)"
                      :key="id" class="tag">
                  <router-link :to="{ name: t, params: { model: currentModel.short_name, id } }">
                    {{ id }}
                  </router-link>
                </span>
              </div>
            </li>
          </ul>
        </div>
      </div>
      <div v-else class="content">
        <loader />
      </div>
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
      types: {
        reaction: 'Reaction',
        metabolite: 'CompartmentalizedMetabolite',
      },
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

      const models = this.comparisonDetails.models.models.map(m => this.modelList.find(mo => mo.apiName === m.model));
      return models.map(m => m.short_name).join(' and ');
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
