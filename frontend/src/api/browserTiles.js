import axios from 'axios';

// params: { model, version }
const fetchBrowserTiles = async (params) => {
  const { data } = await axios.get('/random-components', { params });
  return data;
};

export default { fetchBrowserTiles };
