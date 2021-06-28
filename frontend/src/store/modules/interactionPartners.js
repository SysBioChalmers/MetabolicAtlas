/* eslint-disable no-unused-vars */

import interactionPartnersApi from '@/api/interactionPartners';
import randomComponentsApi from '@/api/randomComponents';
import { chemicalName } from '@/helpers/chemical-formatters';
import { constructCompartmentStr } from '@/helpers/utils';

const data = {
  interactionPartners: {},
  tooLargeNetworkGraph: false,
  expansion: {},
  randomComponents: null,
};

const getters = {
  component: state => state.interactionPartners.component || {},
  reactions: state => state.interactionPartners.reactions || [],
  title: (state, _getters) => (_getters.component.type === 'metabolite'
    ? chemicalName(_getters.component.name) || _getters.component.id
    : _getters.component.name || _getters.component.id
  ),
  reactionsSet: (state, _getters) => new Set(_getters.reactions.map(r => r.id)),
  componentName: (state, _getters) => _getters.component.name || _getters.component.id,
};

const formatInteractionPartners = ips => ({
  ...ips,
  reactions: ips.reactions.map(r => ({
    ...r,
    compartment: constructCompartmentStr(r),
    reactants: r.metabolites.filter(m => m.outgoing),
    products: r.metabolites.filter(m => !m.outgoing),
  })),
});

const actions = {
  async getInteractionPartners({ commit }, { model, id }) {
    const payload = { id, version: model.apiVersion, model: model.apiName };
    const interactionPartners = await interactionPartnersApi.fetchInteractionPartners(payload);

    commit('setTooLargeNetworkGraph', !interactionPartners.reactions);
    commit('setInteractionPartners', formatInteractionPartners(interactionPartners));
  },

  async getRandomComponents({ commit }, model) {
    commit('setRandomComponents', null);
    const payload = {
      model: model.apiName,
      version: model.apiVersion,
      componentTypes: { gene: true, compartmentalizedMetabolite: true },
    };
    const randomComponents = await randomComponentsApi.fetchRandomComponents(payload);
    commit('setRandomComponents', randomComponents);
  },

  async loadExpansion(args, { model, id }) {
    const { state, commit } = args;
    const _getters = args.getters; // eslint-disable-line no-underscore-dangle

    const payload = { id, version: model.apiVersion, model: model.apiName };
    let expansion = await interactionPartnersApi.fetchInteractionPartners(payload);
    expansion = formatInteractionPartners(expansion);

    commit('setTooLargeNetworkGraph', !expansion.reactions);
    commit('setExpansion', expansion);

    const newReactions = expansion.reactions.filter(r => !_getters.reactionsSet.has(r.id));
    const updatedInteractionPartners = {
      ...state.interactionPartners,
      reactions: [..._getters.reactions, ...newReactions],
    };

    commit('setInteractionPartners', updatedInteractionPartners);
  },
};

const mutations = {
  setInteractionPartners: (state, interactionPartners) => {
    state.interactionPartners = interactionPartners;
  },
  setTooLargeNetworkGraph: (state, tooLargeNetworkGraph) => {
    state.tooLargeNetworkGraph = tooLargeNetworkGraph;
  },
  setExpansion: (state, expansion) => {
    state.expansion = expansion;
  },
  setRandomComponents: (state, randomComponents) => {
    state.randomComponents = randomComponents;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
