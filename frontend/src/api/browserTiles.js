import axios from 'axios';

const fetchBrowserTiles = async ({ model, version }) => {
  const params = { model, version };
  const { data } = await axios.get('/random-components', { params });
  return { model, version, ...data };
};

export default { fetchBrowserTiles };
