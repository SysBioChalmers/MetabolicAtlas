import axios from 'axios';

const baseURL = '/api/v2/';

const fetchAvailableMaps = async (model, mapType, id) => {
  const { data } = await axios({ url: `${model}/available_maps/${mapType}/${id}`, baseURL });
  return data;
};

const fetchMapsListing = async (model) => {
  const { data } = await axios({ url: `${model}/viewer/`, baseURL });
  return data;
};

const fetchSvgMap = async (mapUrl, model, svgName) => {
  const { data } = await axios({ url: `${mapUrl}/${model}/${svgName}`, baseURL });
  return data;
};

const mapSearch = async (model, searchTerm) => {
  const { data } = await axios({ url: `${model}/get_id/${searchTerm}`, baseURL });
  return data;
};

const fetch3DMapNetwork = async (model, type, name) => {
  const { data } = await axios({ url: `/${model}/json/${type}/${name}`, baseURL });
  return data;
};

export default { fetchAvailableMaps, fetchMapsListing, fetchSvgMap, mapSearch, fetch3DMapNetwork };
