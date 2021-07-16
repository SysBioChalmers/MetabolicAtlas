import axios from 'axios';

const fetchGeneData = async ({ id, model, version }) => {
  const params = { model, version };
  const { data } = await axios.get(`/genes/${id}`, { params });
  return { ...data, geneName: data.name || data.id };
};

export default { fetchGeneData };
