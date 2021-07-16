import querySingleResult from 'neo4j/queryHandlers/single';

const COMPONENT_TYPES = ['Reaction', 'CompartmentalizedMetabolite'];

const compareTwo = async ({ type, models }) => {
  const [ma, mb] = models;

  const aStatement = `
MATCH (a:${type}:${ma.model})-[:V${ma.version}]-()
RETURN { ${ma.model}: COUNT(DISTINCT(a)) }
`;

  const bStatement = `
MATCH (b:${type}:${mb.model})-[:V${mb.version}]-()
RETURN { ${mb.model}: COUNT(DISTINCT(b)) }
`;

  const compareStatement = `
MATCH (a:${type}:${ma.model})-[:V${ma.version}]-(:ExternalDb)-[:V${mb.version}]-(b:${type}:${mb.model})
RETURN { ${ma.model}: COUNT(DISTINCT(a)), ${mb.model}: COUNT(DISTINCT(b)) }
`;

  const promises = [
    querySingleResult(aStatement, false),
    querySingleResult(bStatement, false),
    querySingleResult(compareStatement, false),
  ];

  return Promise.all(promises);
};

const compareThree = async ({ type, models }) => {
  const [ma, mb, mc] = models;

  const statement = `
MATCH (a:${type}:${ma.model})-[:V${ma.version}]-(e:ExternalDb)-[:V${mb.version}]-(b:${type}:${mb.model})
MATCH (a)-[:V${ma.version}]-(e)-[:V${mc.version}]-(c:${type}:${mc.model})
MATCH (b)-[:V${mb.version}]-(e)-[:V${mc.version}]-(c)
RETURN { ${ma.model}: COUNT(DISTINCT(a)), ${mb.model}: COUNT(DISTINCT(b)), ${mc.model}: COUNT(DISTINCT(c)) }
`;

  const promises = [
    compareTwo({ type, models: [ma, mb] }),
    compareTwo({ type, models: [ma, mc] }),
    compareTwo({ type, models: [mb, mc] }),
    querySingleResult(statement, false),
  ];

  const results = await Promise.all(promises);
  const filteredResults = results.flat() // remove duplicates
    .filter((v, i, a) => a.findIndex(r => JSON.stringify(r) === JSON.stringify(v)) === i);;

  return filteredResults.sort((a, b) => Object.keys(a).length - Object.keys(b).length);
  ;
};

const compareFour = async ({ type, models }) => {
  const [ma, mb, mc, md] = models;

  const statement = `
MATCH (a:${type}:${ma.model})-[:V${ma.version}]-(e:ExternalDb)-[:V${mb.version}]-(b:${type}:${mb.model})
MATCH (a)-[:V${ma.version}]-(e)-[:V${mc.version}]-(c:${type}:${mc.model})
MATCH (a)-[:V${ma.version}]-(e)-[:V${md.version}]-(d:${type}:${md.model})
MATCH (b)-[:V${mb.version}]-(e)-[:V${mc.version}]-(c)
MATCH (b)-[:V${mb.version}]-(e)-[:V${md.version}]-(d)
MATCH (c)-[:V${mc.version}]-(e)-[:V${md.version}]-(d)
RETURN { ${ma.model}: COUNT(DISTINCT(a)), ${mb.model}: COUNT(DISTINCT(b)), ${mc.model}: COUNT(DISTINCT(c)), ${md.model}: COUNT(DISTINCT(d)) }
`;

  const promises = [
    compareThree({ type, models: [ma, mb, mc] }),
    compareThree({ type, models: [ma, mb, md] }),
    compareThree({ type, models: [ma, mc, md] }),
    compareThree({ type, models: [mb, mc, md] }),
    querySingleResult(statement, false),
  ];

  const results = await Promise.all(promises);
  const filteredResults = results.flat() // remove duplicates
    .filter((v, i, a) => a.findIndex(r => JSON.stringify(r) === JSON.stringify(v)) === i);;

  return filteredResults.sort((a, b) => Object.keys(a).length - Object.keys(b).length);
};

const compareOverview = async ({ models, type }) => {
  const max = type === 'CompartmentalizedMetabolite' ? 3 : 4;

  if (models.length < 2 || models.length > max) {
    throw new Error(`At least 2 and at most ${max} models need to be provided for ${type}.`);
  }

  const payload = { type, models };

  if (models.length === 2) {
    return await compareTwo(payload);
  }

  if (models.length === 3) {
    return await compareThree(payload);
  }
  
  return compareFour(payload);
};

const compareDetails = async({ model, models, type }) => {
  // models can be of length 1 or 2
  const [ma, mb, mc] = [model, ...models];

  const selfStatement = `
MATCH (a:${type}:${ma.model})-[:V${ma.version}]-()
RETURN { own: COUNT(DISTINCT(a)) }
`;

  let commonStatement, uniqueStatement;

  if (mc) {
    commonStatement = `
MATCH (a:${type}:${ma.model})-[:V${ma.version}]-(e:ExternalDb)-[:V${mb.version}]-(b:${type}:${mb.model})
MATCH (a)-[:V${ma.version}]-(e)-[:V${mc.version}]-(c:${type}:${mc.model})
MATCH (b)-[:V${mb.version}]-(e)-[:V${mc.version}]-(c)
RETURN { common: COUNT(DISTINCT(a)) }
`;

    uniqueStatement = `
MATCH (a:${type}:${ma.model})-[:V${ma.version}]-()
WHERE NOT (a)-[:V${ma.version}]-(:ExternalDb)-[:V${mb.version}]-(:${type}:${mb.model})
AND NOT (a)-[:V${ma.version}]-(:ExternalDb)-[:V${mc.version}]-(:${type}:${mc.model})
RETURN { unique: COLLECT(DISTINCT(a.id)) }
`;
  } else {
    commonStatement = `
MATCH (a:${type}:${ma.model})-[:V${ma.version}]-(:ExternalDb)-[:V${mb.version}]-(b:${type}:${mb.model})
RETURN { common: COUNT(DISTINCT(a)) }
`;

    uniqueStatement = `
MATCH (a:${type}:${ma.model})-[:V${ma.version}]-()
WHERE NOT (a)-[:V${ma.version}]-(:ExternalDb)-[:V${mb.version}]-(:${type}:${mb.model})
RETURN { unique: COLLECT(DISTINCT(a.id)) }
`;
  }

  const promises = [
    querySingleResult(selfStatement, false),
    querySingleResult(commonStatement, false),
    querySingleResult(uniqueStatement, false),
  ];

  const results = await Promise.all(promises);
  return results.reduce((obj, x) => ({ ...obj, ...x }), {})
};

const getComparisonOverview = async({ models }) => {
  const results = await Promise.all(COMPONENT_TYPES.map(async type => ({
    [type]: await compareOverview({ models, type })
  })));

  return results.reduce((obj, x) => ({ ...obj, ...x }), {});
};

const getComparisonDetails = async({ model, models }) => {
  const promises = COMPONENT_TYPES.map(async type => ({
    [type]: await compareDetails({ model, models, type })
  }));
  const results = await Promise.all(promises);

  return {
    models: { model, models },
    details: results.reduce((obj, x) => ({ ...obj, ...x }), {}),
  };
};

export { getComparisonOverview, getComparisonDetails };
