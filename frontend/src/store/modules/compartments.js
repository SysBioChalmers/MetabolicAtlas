import compartmentsApi from '@/api/compartments';

const data = {
  compartmentSummary: {},
};

const getters = {
  info: state => state.compartmentSummary.info || {},
  subsystems: state => state.compartmentSummary.subsystems || [],
};

const actions = {
  async getCompartmentSummary({ commit }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion };
    const compartmentSummary = await compartmentsApi.fetchCompartmentSummary(payload);
    commit('setCompartmentSummary', compartmentSummary);

    commit('maps/setAvailableMaps', {
      '2d': {
        compartment: compartmentSummary.compartmentSVGs,
        subsystem: [],
      },
      '3d': { compartment: [{ id: compartmentSummary.info.id, customName: compartmentSummary.info.name }], subsystem: [] },
    }, { root: true });
  },
};

const mutations = {
  setCompartmentSummary: (state, compartmentSummary) => {
    state.compartmentSummary = compartmentSummary;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
