import axios from 'axios';

const fetchRnaLevels = async () => {
  const { data } = await axios.get('/rna/all/');
  return data;
};

export default { fetchRnaLevels };
