import externalDbApi from '@/api/externalDb';

const data = {
  components: [],
  externalDb: null,
};

const actions = {
  async getComponentsForExternalDb({ commit }, { dbName, externalId }) {
    const { components, externalDb } = await externalDbApi.fetchComponentsForExternalDb({ dbName, externalId });
    commit('setComponents', components);
    commit('setExternalDb', externalDb);
  },
};

const mutations = {
  setComponents: (state, components) => {
    state.components = components;
  },
  setExternalDb: (state, externalDb) => {
    state.externalDb = externalDb;
  },
};

export default {
  namespaced: true,
  state: data,
  actions,
  mutations,
};
