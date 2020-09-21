import modelsApi from '@/api/models';

const data = {
  model: null,
  modelList: [],
};

const getters = {
  models: state => state.modelList.reduce((models, model) => {
    const modifiedModel = {
      ...model,
      email: model.authors[0].email,
    };
    return {
      ...models,
      [model.short_name]: modifiedModel,
    };
  }, {}),
  integratedModels: state => state.modelList.map(model => ({
    ...model,
    sample: [
      model.sample.tissue,
      model.sample.cell_type,
      model.sample.cell_line,
    ].filter(e => e).join(' ‒ ') || '-',
  })).sort((a, b) => (a.short_name.toLowerCase() < b.short_name.toLowerCase() ? 1 : -1)),
};

const actions = {
  async getModels({ commit }) {
    const models = await modelsApi.fetchModels();
    commit('setModelList', models);
  },
  /* eslint-disable no-shadow */
  async selectModel({ dispatch, commit, getters, state }, modelShortName) {
    if (state.modelList.length === 0) {
      await dispatch('getModels');
    }
    const fixedModels = getters.models;
    const modelShortNamesDict = {};
    Object.values(fixedModels).forEach((m) => { modelShortNamesDict[m.short_name] = m; });
    if (modelShortName in modelShortNamesDict) {
      commit('setModel', fixedModels[modelShortName]);
      return true;
    }
    return false;
  },
};

const mutations = {
  setModel: (state, model) => {
    state.model = model;
  },
  setModelList: (state, modelList) => {
    state.modelList = modelList;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
