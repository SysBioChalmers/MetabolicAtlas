import axios from 'axios';

const fetchInteractionPartners = async ({ id, model, version }) => {
  const params = { model, version };
  const { data } = await axios.get(`/interaction-partners/${id}`, { params });
  return data;
};

export default { fetchInteractionPartners };
