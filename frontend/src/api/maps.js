import axios from 'axios';

const fetchMapsListing = async ({ model, version }) => {
  const params = { model, version };
  const { data } = await axios.get('/maps/listing', { params });
  return data;
};

const fetchSvgMap = async (model, svgName) => {
  const { data } = await axios({ url: `svg/${model}/${svgName}` });
  return data;
};

const mapSearch = async ({ searchTerm, model, version }) => {
  const params = { searchTerm, model, version };
  const { data } = await axios.get('/maps/search', { params });
  return data;
};

const fetch3DMapNetwork = async ({ model, version, type, id }) => {
  const params = { model, version, type, id };
  const { data } = await axios.get('/3d-network', { params });
  return data;
};

export default { fetchMapsListing, fetchSvgMap, mapSearch, fetch3DMapNetwork };
