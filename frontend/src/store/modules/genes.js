import genesApi from '@/api/genes';

const data = {
  gene: {},
};

const getters = {
  geneName: state => state.gene.id,
};

const actions = {
  async getGeneData({ commit }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion };
    const gene = await genesApi.fetchGeneData(payload);
    commit('setGene', gene);
    commit('maps/setAvailableMaps', {
      '2d': {
        compartment: gene.compartmentSVGs,
        subsystem: gene.subsystemSVGs,
      },
      '3d': {
        compartment: gene.compartments.map(c => ({ id: c.id, customName: c.name })),
        subsystem: gene.subsystems.map(s => ({ id: s.id, customName: s.name })),
      },
    }, { root: true });
  },
};

const mutations = {
  setGene: (state, gene) => {
    state.gene = gene;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
