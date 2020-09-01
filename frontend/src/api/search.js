import axios from 'axios';

// params: { searchTerm, model, version, limit }
const search = async (params) => {
  const { data } = await axios.get('/search', { params });
  return data;
};

export default { search };
