import axios from 'axios';

const fetchComparisons = async ({ models }) => {
  const params = { models: JSON.stringify(models) };
  const { data } = await axios.get('/compare', { params });
  return data;
};

const fetchComparisonDetails = async ({ model, models }) => {
  const params = {
    model: JSON.stringify(model),
    models: JSON.stringify(models),
  };
  const { data } = await axios.get('/comparison-details', { params });
  return data;
};

export default { fetchComparisons, fetchComparisonDetails };
