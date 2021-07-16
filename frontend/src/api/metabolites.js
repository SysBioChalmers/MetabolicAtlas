import axios from 'axios';

const fetchMetaboliteData = async ({ id, model, version }) => {
  const params = { model, version };
  const { data } = await axios.get(`/metabolites/${id}`, { params });
  return data;
};

const fetchRelatedMetabolites = async ({ id, model, version }) => {
  const params = { model, version };
  const { data } = await axios.get(`/metabolites/${id}/related-metabolites`, { params });
  return data.sort((a, b) => (a.compartment_str < b.compartment_str ? -1 : 1));
};

export default {
  fetchMetaboliteData,
  fetchRelatedMetabolites,
};
