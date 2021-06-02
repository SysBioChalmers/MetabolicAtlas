import querySingleResult from 'neo4j/queryHandlers/single';

const getComponentsForExternalDb = async ({ dbName, externalId }) => {
  const statement = `
MATCH (db:ExternalDb {dbName: '${dbName}', externalId: '${externalId}'})-[v]-(c)
RETURN { externalDb: properties(db), components: COLLECT({ component: c, version: type(v) }) }
`;

  let { externalDb, components } = await querySingleResult(statement);

  components = components.map(({ component, version }) => {
    const { labels, properties } = component;
    const model = labels.find(l => l.indexOf('Gem') > -1).replace('Gem', '-GEM');
    const componentType = labels.find(l => l.indexOf('Gem') === -1);

    return {
      id: properties.id,
      model,
      componentType,
      version: version.replace('V', '').replace(/_/g, '.'),
    };
  });

  return { components, externalDb };
};

export default getComponentsForExternalDb;
