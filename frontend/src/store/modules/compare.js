import compareApi from '@/api/compare';

const data = {
  comparisons: [],
};

const actions = {
  async getComparisons({ commit }, { type, models }) {
    const payload = { type, models };
    const comparisons = await compareApi.fetchComparisons(payload);
    commit('setComparisons', comparisons);
  },
  resetComparisons({ commit }) {
    commit('setComparisons', []);
  },
};

const mutations = {
  setComparisons: (state, comparisons) => {
    state.comparisons = comparisons;
  },
};

export default {
  namespaced: true,
  state: data,
  actions,
  mutations,
};
