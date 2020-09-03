import axios from 'axios';

const baseURL = '/api/v2/';

const fetchMapsListing = async ({ model, version }) => {
  const params = { model, version };
  const { data } = await axios.get('/maps/listing', { params });

  const compartment = data.compartments.map(c => ({
    id: c.id,
    name: c.name,
    compartment_svg: c.compartmentSVGs.length === 0 ? null : c.compartmentSVGs[0].id,
    reaction_count: c.reactionCount,
  }));

  const compartmentsvg = data.compartments.reduce((l, c) => {
    const svgs = c.compartmentSVGs.map(svg => (
      {
        id: svg.id,
        name: svg.customName,
        compartment: c.id,
        filename: svg.filename,
      }));
    return [...l, svgs];
  }, []).flat();

  const subsystem = data.subsystems.map(s => ({
    id: s.id,
    name: s.name,
    subsystem_svg: s.subsystemSVGs.length === 0 ? null : s.subsystemSVGs[0].id,
    reaction_count: s.reactionCount,
  }));

  const subsystemsvg = data.subsystems.reduce((l, s) => {
    const svgs = s.subsystemSVGs.map(svg => (
      {
        id: svg.id,
        name: svg.customName,
        subsystem: s.id,
        filename: svg.filename,
      }));
    return [...l, svgs];
  }, []).flat();

  return { compartment, compartmentsvg, subsystem, subsystemsvg };
};

const fetchSvgMap = async (mapUrl, model, svgName) => {
  const { data } = await axios({ url: `${mapUrl}/${model}/${svgName}`, baseURL });
  return data;
};

const mapSearch = async ({ searchTerm, model, version }) => {
  const params = { searchTerm, model, version };
  const { data } = await axios.get('/maps/search', { params });
  return data;
};

const fetch3DMapNetwork = async (model, type, name) => {
  const { data } = await axios({ url: `/${model}/json/${type}/${name}`, baseURL });
  return data;
};

export default { fetchMapsListing, fetchSvgMap, mapSearch, fetch3DMapNetwork };
