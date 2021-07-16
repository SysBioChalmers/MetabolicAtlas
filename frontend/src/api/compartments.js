import axios from 'axios';

const fetchCompartmentSummary = async ({ id, model, version }) => {
  const params = { model, version };
  const { data } = await axios.get(`/compartments/${id}`, { params });
  return data;
};

export default { fetchCompartmentSummary };
