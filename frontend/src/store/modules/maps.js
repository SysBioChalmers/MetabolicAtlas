import mapsApi from '@/api/maps';
import genesApi from '@/api/genes';
import reactionsApi from '@/api/reactions';
import metabolitesApi from '@/api/metabolites';

const data = {
  availableMaps: {},
  mapsListing: {
    compartments: [],
    subsystems: [],
  },
  svgMap: null,
  idsFound: [],
  selectedElement: null,
  network: {
    nodes: [],
    links: [],
  },
  showing2D: true,
  dataOverlayPanelVisible: false,
  coords: {
    x: 0,
    y: 0,
    z: 1,
    lx: 0,
    ly: 0,
    lz: 0,
  },
  searchTerm: '',
  selectedElementId: null,
  tissue1: null,
  tissue2: null,
};

const getters = {
  mapsListing: state => state.mapsListing,

  selectIds: state => [state.selectedElementId].filter(x => x),

  queryParams: state => ({
    dim: state.showing2D ? '2d' : '3d',
    panel: +state.dataOverlayPanelVisible,
    sel: state.selectedElementId,
    search: state.searchTerm,
    coords: Object.values(state.coords).map(c => Math.round((c + Number.EPSILON) * 100) / 100).join(','),
    g1: state.tissue1,
    g2: state.tissue2,
  }),
};

const actions = {
  async getAvailableMaps({ commit }, { model, mapType, id }) {
    const maps = await mapsApi.fetchAvailableMaps(model, mapType, id);
    commit('setAvailableMaps', maps);
  },

  async getMapsListing({ commit }, model) {
    const payload = { model: model.apiName, version: model.apiVersion };
    const mapsListing = await mapsApi.fetchMapsListing(payload);
    commit('setMapsListing', mapsListing);
  },

  async getSvgMap({ commit }, { mapUrl, model, svgName }) {
    const svgMap = await mapsApi.fetchSvgMap(mapUrl, model, svgName);
    commit('setSvgMap', svgMap);
  },

  setSvgMap({ commit }, svgMap) {
    commit('setSvgMap', svgMap);
  },

  async mapSearch({ commit }, { model, searchTerm }) {
    commit('setSearchTerm', searchTerm);
    const payload = { model: model.apiName, version: model.apiVersion, searchTerm };
    const idsFound = await mapsApi.mapSearch(payload);
    commit('setIdsFound', idsFound);
  },

  clearSearchTerm({ commit }) {
    commit('setSearchTerm', '');
  },

  setIdsFound({ commit }, idsFound) {
    commit('setIdsFound', idsFound);
  },

  async getSelectedElement({ commit }, { model, type, id }) {
    let apiFunc;

    switch (type) {
      case 'gene':
        apiFunc = genesApi.fetchGeneData;
        break;
      case 'reaction':
        apiFunc = reactionsApi.fetchReactionData;
        break;
      case 'metabolite':
        apiFunc = metabolitesApi.fetchMetaboliteData;
        break;
      default:
        // TODO: handle unexpected type
        break;
    }

    const selectedElement = await apiFunc(model, id);
    commit('setSelectedElementId', id);
    commit('setSelectedElement', selectedElement);
  },

  async get3DMapNetwork({ commit }, { model, version, type, id }) {
    const network = await mapsApi.fetch3DMapNetwork({ model, version, type, id });
    commit('setNetwork', network);
  },

  set3DMapNetwork({ commit }, network) {
    commit('setNetwork', network);
  },

  setShowing2D({ commit }, showing2D) {
    commit('setShowing2D', showing2D);
  },

  toggleDataOverlayPanelVisible({ state, commit }) {
    commit('setDataOverlayPanelVisible', !state.dataOverlayPanelVisible);
  },

  setDataOverlayPanelVisible({ commit }, dataOverlayPanelVisible) {
    commit('setDataOverlayPanelVisible', dataOverlayPanelVisible);
  },

  setCoords({ commit }, coords) {
    commit('setCoords', coords);
  },

  setSelectedElementId({ commit }, selectedElementId) {
    commit('setSelectedElementId', selectedElementId);
  },

  setTissue1({ commit }, tissue1) {
    commit('setTissue1', tissue1);
  },

  setTissue2({ commit }, tissue2) {
    commit('setTissue2', tissue2);
  },

  initFromQueryParams({ commit }, { dim, panel, coords, sel, search, g1, g2 }) {
    // TODO: handle errors
    commit('setShowing2D', dim === '2d');
    commit('setDataOverlayPanelVisible', !!(panel === '1' || g1 || g2));
    commit('setSelectedElementId', sel);
    commit('setSearchTerm', search);

    if (coords && coords.length > 0) {
      const parsedCoords = coords.split(',').map(c => parseFloat(c));
      commit('setCoords', {
        x: parsedCoords[0],
        y: parsedCoords[1],
        z: parsedCoords[2],
        lx: parsedCoords[3],
        ly: parsedCoords[4],
        lz: parsedCoords[5],
      });
    }

    if (g1 && g1.length > 0) {
      commit('setTissue1', g1);
    }

    if (g2 && g2.length > 0) {
      commit('setTissue2', g2);
    }
  },

  resetParamsExcept({ commit }, paramsToKeep) {
    if (!paramsToKeep.includes('dim')) {
      commit('setShowing2D', true);
    }

    if (!paramsToKeep.includes('panel')) {
      commit('setDataOverlayPanelVisible', false);
    }

    if (!paramsToKeep.includes('sel')) {
      commit('setSelectedElementId', null);
    }

    if (!paramsToKeep.includes('search')) {
      commit('setSearchTerm', '');
    }

    if (!paramsToKeep.includes('coords')) {
      commit('setCoords', {
        x: 0,
        y: 0,
        z: 1,
        lx: 0,
        ly: 0,
        lz: 0,
      });
    }

    if (!paramsToKeep.includes('g1')) {
      commit('setTissue1', null);
    }

    if (!paramsToKeep.includes('g2')) {
      commit('setTissue2', null);
    }
  },
};

const mutations = {
  setAvailableMaps: (state, maps) => {
    state.availableMaps = maps;
  },

  setMapsListing: (state, mapsListing) => {
    state.mapsListing = mapsListing;
  },

  setSvgMap: (state, svgMap) => {
    state.svgMap = svgMap;
  },

  setIdsFound: (state, idsFound) => {
    state.idsFound = idsFound;
  },

  setSelectedElement: (state, selectedElement) => {
    state.selectedElement = selectedElement;
  },

  setNetwork: (state, network) => {
    state.network = network;
  },

  setShowing2D: (state, showing2D) => {
    state.showing2D = showing2D;
  },

  setDataOverlayPanelVisible: (state, dataOverlayPanelVisible) => {
    state.dataOverlayPanelVisible = dataOverlayPanelVisible;
  },

  setCoords: (state, coords) => {
    state.coords = coords;
  },

  setSelectedElementId: (state, selectedElementId) => {
    state.selectedElementId = selectedElementId;
  },

  setSearchTerm: (state, searchTerm) => {
    state.searchTerm = searchTerm;
  },

  setTissue1: (state, tissue1) => {
    state.tissue1 = tissue1;
  },

  setTissue2: (state, tissue2) => {
    state.tissue2 = tissue2;
  },
};

export default {
  namespaced: true,
  state: data,
  getters,
  actions,
  mutations,
};
