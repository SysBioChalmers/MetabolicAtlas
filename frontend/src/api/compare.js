import axios from 'axios';

const fetchComparisons = async ({ models }) => {
  const params = { models: JSON.stringify(models) };
  const { data } = await axios.get('/compare', { params });
  return data;
};

export default { fetchComparisons };
