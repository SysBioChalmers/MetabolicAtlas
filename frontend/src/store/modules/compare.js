import compareApi from '@/api/compare';

const data = {
  comparisons: {
    reactions: [],
    metabolites: [],
  },
};

const actions = {
  async getComparisons({ commit }, { models }) {
    const [reactions, metabolites] = await compareApi.fetchComparisons({ models });

    commit('setComparisons', { reactions, metabolites });
  },
  resetComparisons({ commit }) {
    commit('setComparisons', []);
  },
};

const getters = {
  comparisonsEmpty: state => Object.values(state.comparisons).flat().length === 0,
};

const mutations = {
  setComparisons: (state, comparisons) => {
    state.comparisons = comparisons;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
