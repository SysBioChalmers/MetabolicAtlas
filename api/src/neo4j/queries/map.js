import queryListResult from 'neo4j/queryHandlers/list';

const getMapsListing = async ({ model, version }) => {
  const m = model;
  const v = version;

  const statement = `
MATCH (:CompartmentState)-[:V${v}]-(c:Compartment:${m})
CALL apoc.cypher.run("
  MATCH (cs:CompartmentState)-[:V${v}]-(:Compartment:${m} {id: $cid})
  RETURN cs { id: $cid, .* } as data
  
  UNION
  
  MATCH (:Compartment:${m} {id: $cid})-[:V${v}]-(:CompartmentalizedMetabolite)-[:V${v}]-(r:Reaction)
  RETURN { id: $cid, reactionCount: COUNT(DISTINCT(r)) } as data
  
  UNION
  
  MATCH (csvg:SvgMap)-[:V${v}]-(:Compartment:${m} {id: $cid})
  RETURN { id: $cid, compartmentSVGs: COLLECT(DISTINCT(csvg {.*})) } as data
", {cid:c.id}) yield value
RETURN { compartment: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as data

UNION

MATCH (:SubsystemState)-[:V${v}]-(s:Subsystem:${m})
CALL apoc.cypher.run("
  MATCH (ss:SubsystemState)-[:V${v}]-(s:Subsystem {id: $sid})
  RETURN ss { id: $sid, .* } as data
  
  UNION
  
  MATCH (:Subsystem:${m} {id: $sid})-[:V${v}]-(r:Reaction)
  RETURN { id: $sid, reactionCount: COUNT(DISTINCT(r)) } as data
  
  UNION
  
  MATCH (:Subsystem:${m} {id: $sid})-[:V${v}]-(ssvg:SvgMap)
  RETURN { id: $sid, subsystemSVGs: COLLECT(DISTINCT(ssvg {.*})) } as data
", {sid:s.id}) yield value
RETURN { subsystem: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as data
`;

  const result = await queryListResult(statement);

  const mapListing = {
    compartments: result.filter(o => !!o.compartment).reduce((l, o) => [...l, o.compartment] , []),
    subsystems: result.filter(o => !!o.subsystem).reduce((l, o) => [...l, o.subsystem] , []),
  };

  return mapListing;
};

export default getMapsListing;
