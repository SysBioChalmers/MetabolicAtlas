import axios from 'axios';

const fetchComparisons = async ({ type, models }) => {
  const params = { type, models: JSON.stringify(models) };
  const { data } = await axios.get('/compare', { params });
  return data;
};

export default { fetchComparisons };
