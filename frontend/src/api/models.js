import axios from 'axios';

const fetchModels = async () => {
  const { data } = await axios.get('repository/integrated_models/');
  return data;
};

export default { fetchModels };
