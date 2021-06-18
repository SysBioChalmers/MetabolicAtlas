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

    commit('maps/setAvailableMaps', [
      ...gene.compartmentSVGs, ...gene.subsystemSVGs,
    ], { root: true });
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
