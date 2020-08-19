import reactionsApi from '@/api/reactions';
import { constructCompartmentStr } from '@/helpers/utils';

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

    commit('setReaction', {
      ...reaction,
      compartment_str: reaction.compartments.map(c => c.name).join(', '),
      reactionreactant_set: reaction.metabolites.filter(m => m.outgoing),
      reactionproduct_set: reaction.metabolites.filter(m => !m.outgoing),
    });

    commit('maps/setAvailableMaps', {
      '2d': {
        compartment: reaction.compartmentSVGs,
        subsystem: reaction.subsystemSVGs,
      },
      '3d': {
        compartment: reaction.compartments.map(c => ({ id: c.id, customName: c.name })),
        subsystem: reaction.subsystems.map(s => ({ id: s.id, customName: s.name })),
      },
    }, { root: true });

    const pmids = pubmedIds.map(pm => pm.id);
    commit('setReferenceList', pmids);
  },
  async getRelatedReactionsForReaction({ commit, state }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion, limit: state.relatedReactionsLimit };
    const reactions = await reactionsApi.fetchRelatedReactionsForReaction(payload);
    commit(
      'setRelatedReactions',
      reactions.map(r => ({
        ...r,
        compartment_str: constructCompartmentStr(r),
        reactionreactant_set: r.metabolites.filter(m => m.outgoing),
        reactionproduct_set: r.metabolites.filter(m => !m.outgoing),
      }))
    );
  },
  async getRelatedReactionsForGene({ commit, state }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion, limit: state.relatedReactionsLimit };
    const reactions = await reactionsApi.fetchRelatedReactionsForGene(payload);
    commit(
      'setRelatedReactions',
      reactions.map(r => ({
        ...r,
        compartment_str: constructCompartmentStr(r),
        subsystem_str: r.subsystems.map(s => s.name).join(', '),
        reactionreactant_set: r.metabolites.filter(m => m.outgoing),
        reactionproduct_set: r.metabolites.filter(m => !m.outgoing),
      }))
    );
    // commit('setRelatedReactionsLimit', limit);
  },
  async getRelatedReactionsForMetabolite({ commit, state }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion, limit: state.relatedReactionsLimit };
    const reactions = await reactionsApi.fetchRelatedReactionsForMetabolite(payload);

    commit(
      'setRelatedReactions',
      reactions.map(r => ({
        ...r,
        compartment_str: constructCompartmentStr(r),
        subsystem_str: r.subsystems.map(s => s.name).join(', '),
        reactionreactant_set: r.metabolites.filter(m => m.outgoing),
        reactionproduct_set: r.metabolites.filter(m => !m.outgoing),
      }))
    );
    // commit('setRelatedReactionsLimit', limit);
  },
  async getRelatedReactionsForSubsystem({ commit, state }, { model, id }) {
    const payload = { id, model: model.apiName, version: model.apiVersion, limit: state.relatedReactionsLimit };
    const reactions = await reactionsApi.fetchRelatedReactionsForSubsystem(payload);

    commit(
      'setRelatedReactions',
      reactions.map(r => ({
        ...r,
        compartment_str: constructCompartmentStr(r),
        subsystem_str: r.subsystems.map(s => s.name).join(', '),
        reactionreactant_set: r.metabolites.filter(m => m.outgoing),
        reactionproduct_set: r.metabolites.filter(m => !m.outgoing),
      }))
    );
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
