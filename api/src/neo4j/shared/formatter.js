export const reformatExternalDbs = (externalDbs) => externalDbs.reduce((dbs, db) => {
  let dbRefs = dbs[db.dbName] || [];
  dbRefs = [...dbRefs, { id: db.externalId, url: db.url }];
  return { ...dbs, [db.dbName]: dbRefs };
}, {});

export const reformatCompartmentSVGs = (reaction) => [...reaction.compartments].sort((a, b) => a.id.localeCompare(b.id)).map((c) => {
  const compartmentWithSVGs = reaction.compartmentSVGs.find(({ compartmentId }) => compartmentId === c.id);
  const svgMaps = compartmentWithSVGs ? compartmentWithSVGs.compartmentSVGs.sort((a, b) => a.id.localeCompare(b.id)) : [];
  return {
    id: c.id,
    customName: c.name,
    svgMaps,
  };
})

export const reformatSubsystemSVGs = (reaction) => [...reaction.subsystems].sort((a, b) => a.id.localeCompare(b.id)).map((s) => {
  const subsystemsWithSVGs = reaction.subsystemSVGs.find(({ subsystemId }) => subsystemId === s.id);
  const svgMaps = subsystemsWithSVGs ? subsystemsWithSVGs.subsystemSVGs.sort((a, b) => a.id.localeCompare(b.id)) : [];
  return {
    id: s.id,
    customName: s.name,
    svgMaps,
  };
});
