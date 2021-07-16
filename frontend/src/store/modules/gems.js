import gemsApi from '@/api/gems';

const data = {
  gem: null,
  gems: {},
};

const getters = {
  gemList: state => Object.values(state.gems),
  setFilterOptions: (state, _getters) => [...new Set(_getters.gemList.map(g => g.set_name))].sort(), // eslint-disable-line no-unused-vars
  systemFilterOptions: (state, _getters) => [...new Set(_getters.gemList.map(g => g.organ_system))].sort(), // eslint-disable-line no-unused-vars
  conditionFilterOptions: (state, _getters) => [...new Set(_getters.gemList.map(g => g.condition))].sort(), // eslint-disable-line no-unused-vars
};

const actions = {
  async getGems({ commit }) {
    const gems = await gemsApi.fetchGems();
    commit('setGems', gems);
  },
  getGemData({ commit, state }, id) {
    if (state.gems[id]) {
      commit('setGem', state.gems[id]);
      return true;
    }
    return false;
  },
};

const mutations = {
  setGems: (state, gems) => {
    state.gems = gems;
  },
  setGem: (state, gem) => {
    state.gem = gem;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
