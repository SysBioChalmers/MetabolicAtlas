export const reformatExternalDbs = (externalDbs) => externalDbs.reduce((dbs, db) => {
  let dbRefs = dbs[db.dbName] || [];
  dbRefs = [...dbRefs, { id: db.externalId, url: db.url }];
  return { ...dbs, [db.dbName]: dbRefs };
}, {});

export const reformatCompartmentSVGs = (component) => [...component.compartments].sort((a, b) => a.id.localeCompare(b.id)).map((c) => {
  const compartmentWithSVGs = component.compartmentSVGs.find(({ compartmentId }) => compartmentId === c.id);
  const svgMaps = compartmentWithSVGs ? compartmentWithSVGs.compartmentSVGs.sort((a, b) => a.id.localeCompare(b.id)) : [];
  return {
    id: c.id,
    customName: c.name,
    svgMaps,
  };
})

export const reformatSubsystemSVGs = (component) => [...component.subsystems].sort((a, b) => a.id.localeCompare(b.id)).map((s) => {
  const subsystemsWithSVGs = component.subsystemSVGs.find(({ subsystemId }) => subsystemId === s.id);
  const svgMaps = subsystemsWithSVGs ? subsystemsWithSVGs.subsystemSVGs.sort((a, b) => a.id.localeCompare(b.id)) : [];
  return {
    id: s.id,
    customName: s.name,
    svgMaps,
  };
});
