import axios from 'axios';

const search = async ({ searchTerm, model, version, limit }) => {
  const params = { searchTerm, model, version, limit };
  const { data } = await axios.get('/search', { params });
  return data;
};

export default { search };
