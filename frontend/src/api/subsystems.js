import axios from 'axios';

const fetchSubsystemSummary = async ({ id, model, version }) => {
  const params = { model, version };
  const { data } = await axios.get(`/subsystems/${id}`, { params });
  return data;
};

export default { fetchSubsystemSummary };
