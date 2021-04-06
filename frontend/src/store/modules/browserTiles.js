import randomComponentsApi from '@/api/randomComponents';

const data = {
  tileComponents: null,
};

const actions = {
  async getBrowserTiles({ commit }, model) {
    commit('setTileComponents', null);
    const payload = {
      model: model.apiName,
      version: model.apiVersion,
    };
    const tileComponents = await randomComponentsApi.fetchRandomComponents(payload);
    commit('setTileComponents', tileComponents);
  },
};

const mutations = {
  setTileComponents: (state, tileComponents) => {
    state.tileComponents = tileComponents;
  },
};

export default {
  namespaced: true,
  state: data,
  actions,
  mutations,
};
