import axios from 'axios';

const fetchModels = async () => {
  const { data } = await axios.get('repository/integrated_models/');
  return data.map(m => Object({ ...m, database_name: `${m.short_name.toLowerCase()}` }));
};

export default { fetchModels };
