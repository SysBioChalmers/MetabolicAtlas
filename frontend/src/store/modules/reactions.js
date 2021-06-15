import reactionsApi from '@/api/reactions';

const data = {
  reaction: {},
  referenceList: [],
  relatedReactions: [],
  relatedReactionsLimit: 200,
};

const actions = {
  async getReactionData({ commit }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion };
    const { pubmedIds, ...reaction } = await reactionsApi.fetchReactionData(payload);
    commit('setReaction', reaction);

    commit('maps/setAvailableMaps', [
      ...reaction.compartmentSVGs, ...reaction.subsystemSVGs,
    ], { root: true });

    const pmids = pubmedIds.map(pm => pm.id);
    commit('setReferenceList', pmids);
  },
  async getRelatedReactionsForReaction({ commit, state }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion, limit: state.relatedReactionsLimit };
    const reactions = await reactionsApi.fetchRelatedReactionsForReaction(payload);
    commit('setRelatedReactions', reactions);
  },
  async getRelatedReactionsForGene({ commit, state }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion, limit: state.relatedReactionsLimit };
    const reactions = await reactionsApi.fetchRelatedReactionsForGene(payload);
    commit('setRelatedReactions', reactions);
    // commit('setRelatedReactionsLimit', limit);
  },
  async getRelatedReactionsForMetabolite({ commit, state }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion, limit: state.relatedReactionsLimit };
    const reactions = await reactionsApi.fetchRelatedReactionsForMetabolite(payload);
    commit('setRelatedReactions', reactions);
    // commit('setRelatedReactionsLimit', limit);
  },
  async getRelatedReactionsForSubsystem({ commit, state }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion, limit: state.relatedReactionsLimit };
    const reactions = await reactionsApi.fetchRelatedReactionsForSubsystem(payload);
    commit('setRelatedReactions', reactions);
    // commit('setRelatedReactionsLimit', limit);
  },
  clearRelatedReactions({ commit }) {
    commit('setRelatedReactions', []);
  },
};

const mutations = {
  setReaction: (state, reaction) => {
    state.reaction = reaction;
  },
  setReferenceList: (state, referenceList) => {
    state.referenceList = referenceList;
  },
  setRelatedReactions: (state, reactions) => {
    state.relatedReactions = reactions;
  },
  setRelatedReactionsLimit: (state, limit) => {
    state.relatedReactionsLimit = limit;
  },
};

export default {
  namespaced: true,
  state: data,
  actions,
  mutations,
};
