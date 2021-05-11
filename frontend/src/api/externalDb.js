import axios from 'axios';

const fetchComponentsForExternalDb = async ({ dbName, externalId }) => {
  const { data } = await axios.get(`/external-db/${dbName}/${externalId}`);
  return data;
};

export default { fetchComponentsForExternalDb };
