import axios from 'axios';

const fetchReactionData = async ({ id, model, version }) => {
  const params = { model, version };
  const { data } = await axios.get(`/reactions/${id}`, { params });
  return data;
};

const fetchRelatedReactionsForReaction = async ({ id, model, version, limit }) => {
  const params = { model, version, limit };
  const { data } = await axios.get(`/reactions/${id}/related-reactions`, { params });
  return data.sort((a, b) => (a.compartment_str < b.compartment_str ? -1 : 1));
};

const fetchRelatedReactions = async (resourceType, id, model, version, limit) => {
  const params = { model, version, limit };
  const { data } = await axios.get(`/${resourceType}s/${id}/related-reactions`, { params });
  return data;
};

const fetchRelatedReactionsForGene = async ({ id, model, version, limit }) => fetchRelatedReactions('gene', id, model, version, limit);

const fetchRelatedReactionsForMetabolite = async ({ id, model, version, limit }, allCompartments) => fetchRelatedReactions('metabolite', id, model, version, limit, allCompartments);

const fetchRelatedReactionsForSubsystem = async ({ id, model, version, limit }) => fetchRelatedReactions('subsystem', id, model, version, limit);

export default {
  fetchReactionData,
  fetchRelatedReactionsForReaction,
  fetchRelatedReactionsForGene,
  fetchRelatedReactionsForMetabolite,
  fetchRelatedReactionsForSubsystem,
};
