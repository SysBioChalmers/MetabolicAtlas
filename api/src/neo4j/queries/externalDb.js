import querySingleResult from 'neo4j/queryHandlers/single';

const getComponentsForExternalDb = async ({ dbName, externalId }) => {
  const statement = `
MATCH (db:ExternalDb {dbName: '${dbName}', externalId: '${externalId}'})-[]-(com)
RETURN { externalDb: db, components: COLLECT(com) }
`;

  let { externalDb, components } = await querySingleResult(statement);

  components = components.map(c => {
    const { labels, properties } = c;
    const model = labels.find(l => l.indexOf('Gem') > -1);
    const componentType = labels.find(l => l.indexOf('Gem') === -1);

    return {
      id: properties.id,
      model,
      componentType,
    };
  });

  return {
    components,
    externalDb: externalDb.properties,
  };
};

export default getComponentsForExternalDb;
