import metabolitesApi from '@/api/metabolites';

const data = {
  metabolite: {},
  relatedMetabolites: [],
};

const actions = {
  async getMetaboliteData({ commit }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion };
    const metabolite = await metabolitesApi.fetchMetaboliteData(payload);
    commit('setMetabolite', metabolite);

    commit('maps/setAvailableMaps', [
      ...metabolite.compartmentSVGs, ...metabolite.subsystemSVGs,
    ], { root: true });
  },
  async getRelatedMetabolites({ commit }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion };
    const metabolites = await metabolitesApi.fetchRelatedMetabolites(payload);
    commit('setRelatedMetabolites', metabolites);
  },
  clearRelatedMetabolites({ commit }) {
    commit('setRelatedMetabolites', []);
  },
};

const mutations = {
  setMetabolite: (state, metabolite) => {
    state.metabolite = metabolite;
  },
  setRelatedMetabolites: (state, metabolites) => {
    state.relatedMetabolites = metabolites;
  },
};

export default {
  namespaced: true,
  state: data,
  actions,
  mutations,
};
