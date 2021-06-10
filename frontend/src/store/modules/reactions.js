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

    const compartmentMaps = [...reaction.compartments].sort((a, b) => a.id.localeCompare(b.id)).map((c) => {
      const compartmentWithSVGs = reaction.compartmentSVGs.find(({ compartmentId }) => compartmentId === c.id);
      const svgMaps = compartmentWithSVGs ? compartmentWithSVGs.compartmentSVGs : [];
      return {
        id: c.id,
        customName: c.name,
        svgMaps,
      };
    });
    const subsystemMaps = [...reaction.subsystems].sort((a, b) => a.id.localeCompare(b.id)).map((s) => {
      const subsystemsWithSVGs = reaction.subsystemSVGs.find(({ subsystemId }) => subsystemId === s.id);
      const svgMaps = subsystemsWithSVGs ? subsystemsWithSVGs.subsystemSVGs : [];
      return {
        id: s.id,
        customName: s.name,
        svgMaps,
      };
    });

    commit('maps/setAvailableMaps', [
      ...compartmentMaps, ...subsystemMaps,
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
