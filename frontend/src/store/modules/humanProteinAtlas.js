import hpaApi from '@/api/humanProteinAtlas';

const data = {
  tissues: [],
  levels: {},
};

const getters = {
  HPATissues: state => state.tissues,
};

const actions = {
  async getLevels({ commit }) {
    const tissueLvlDict = await hpaApi.fetchRnaLevels();
    commit('setTissues', tissueLvlDict.tissues);
    commit('setLevels', tissueLvlDict.levels);
  },
};

const mutations = {
  setTissues: (state, tissues) => {
    state.tissues = tissues;
  },
  setLevels: (state, levels) => {
    state.levels = levels;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
