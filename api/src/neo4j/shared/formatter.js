const reformatExternalDbs = (externalDbs) => externalDbs.reduce((dbs, db) => {
  let dbRefs = dbs[db.dbName] || [];
  dbRefs = [...dbRefs, { id: db.externalId, url: db.url }];
  return { ...dbs, [db.dbName]: dbRefs };
}, {});

export default reformatExternalDbs;
