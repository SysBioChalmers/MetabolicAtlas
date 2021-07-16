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
  })),
};

const actions = {
  async getModels({ commit, state }) {
    if (state.modelList.length === 0) {
      const models = await modelsApi.fetchModels();
      commit('setModelList', models.sort((a, b) => (a.short_name.toLowerCase() < b.short_name.toLowerCase() ? -1 : 1)));
    }
  },
  /* eslint-disable no-shadow */
  async selectModel({ dispatch, commit, getters }, modelShortName) {
    await dispatch('getModels');

    if (modelShortName in getters.models) {
      commit('setModel', getters.models[modelShortName]);
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
