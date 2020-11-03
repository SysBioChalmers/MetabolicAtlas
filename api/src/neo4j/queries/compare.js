import querySingleResult from 'neo4j/queryHandlers/single';

const compare = async ({ type, modelA, versionA, modelB, versionB }) => {
  const statement = `
MATCH (ar:${type}:${modelA})-[:V${versionA}]-(:ExternalDb)-[:V${versionB}]-(br:${type}:${modelB})
RETURN { ${modelA}: COUNT(DISTINCT(ar.id)), ${modelB}: COUNT(DISTINCT(br.id)) }
`;

  return querySingleResult(statement);
};

export default compare;
