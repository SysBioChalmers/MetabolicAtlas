import axios from 'axios';

const fetchComponentsForExternalDb = async ({ dbName, externalId }) => {
  const { data } = await axios.get(`/external-db/${dbName}/${externalId}`);
  const { externalDb, components } = data;
  return {
    externalDb,
    components: components.map(c => ({
      ...c,
      componentType: c.componentType.replace('Compartmentalized', ''),
    })),
  };
};

export default { fetchComponentsForExternalDb };
