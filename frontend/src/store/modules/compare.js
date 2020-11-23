import compareApi from '@/api/compare';

const data = {
  comparisons: {
    reactions: [],
    metabolites: [],
  },
  selectedCell: {
    model: null,
    models: [],
    position: {
      row: 1,
      col: 0,
    },
  },
  comparisonDetails: null,
};

const actions = {
  async getComparisons({ commit }, { models }) {
    const comparisons = await compareApi.fetchComparisons({ models });

    commit('setComparisons', {
      reactions: comparisons.Reaction,
      metabolites: comparisons.CompartmentalizedMetabolite,
    });
  },
  async getComparisonDetails({ commit }, { model, models }) {
    commit('setComparisonDetails', null);

    const comparisonDetails = await compareApi.fetchComparisonDetails({ model, models });

    commit('setComparisonDetails', comparisonDetails);
  },
  resetComparisons({ commit }) {
    commit('setComparisons', []);
  },
  resetComparisonDetails({ commit }) {
    commit('setComparisonDetails', null);
  },
  setSelectedCell({ commit }, cell) {
    commit('setSelectedCell', cell);
  },
};

const getters = {
  comparisonsEmpty: state => Object.values(state.comparisons).flat().length === 0,
};

const mutations = {
  setComparisons: (state, comparisons) => {
    state.comparisons = comparisons;
  },
  setComparisonDetails: (state, comparisonDetails) => {
    state.comparisonDetails = comparisonDetails;
  },
  setSelectedCell: (state, selectedCell) => {
    state.selectedCell = selectedCell;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
