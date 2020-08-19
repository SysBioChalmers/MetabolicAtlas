import queryListResult from 'neo4j/queryHandlers/list';
import reformatExternalDbs from 'neo4j/shared/formatter';

const getRandomComponents = async ({ model, version }) => {
  const m = model || 'HumanGem';
  const v = version;

  const statement = `
MATCH (:GeneState)-[:V${v}]-(g:Gene:${m})
WITH g.id as gid, rand() as r
ORDER BY r LIMIT 2
CALL apoc.cypher.run("
  MATCH (gs:GeneState)-[:V${v}]-(:Gene {id: $gid})-[:V${v}]-(re:Reaction)
  RETURN { id: $gid, name: gs.name, reactionCount: COUNT(DISTINCT(re)) } as data
  UNION
  MATCH (:Gene {id: $gid})-[:V${v}]-(:Reaction)-[:V${v}]-(ss:Subsystem)
  RETURN { id: $gid, subsystemCount: COUNT(DISTINCT(ss)) } as data
  UNION
  MATCH (:Gene {id: $gid})-[:V${v}]-(:Reaction)-[:V${v}]-(:CompartmentalizedMetabolite)-[:V${v}]-(c:Compartment)
  RETURN { id: $gid, compartmentCount: COUNT(DISTINCT(c)) } as data
", {gid:gid}) yield value
RETURN { gene: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as xs

UNION

MATCH (:Metabolite)-[:V${v}]-(cm:CompartmentalizedMetabolite:${m})
WITH cm.id as cmid, rand() as r
ORDER BY r LIMIT 2
CALL apoc.cypher.run("
  MATCH (ms:MetaboliteState)-[:V${v}]-(:Metabolite)-[:V${v}]-(:CompartmentalizedMetabolite {id: $cmid})
  RETURN { id: $cmid, name: ms.name, formula: ms.formula } as data
  UNION
  MATCH (re:Reaction)-[:V${v}]-(:CompartmentalizedMetabolite {id: $cmid})
  RETURN { id: $cmid, reactionCount: count(distinct(re)) } as data
  UNION
  MATCH (cs:CompartmentState)-[:V${v}]-(:Compartment)-[:V${v}]-(cm:CompartmentalizedMetabolite {id: $cmid})
  RETURN { id: $cmid, compartment: cs.name } as data
", {cmid:cmid}) yield value
RETURN { metabolite: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as xs

UNION

MATCH (:CompartmentState)-[:V${v}]-(c:Compartment:${m})
WITH c.id as cid, rand() as r
ORDER BY r LIMIT 1
CALL apoc.cypher.run("
  MATCH (cs:CompartmentState)-[:V${v}]-(:Compartment {id: $cid})-[:V${v}]-(:CompartmentalizedMetabolite)-[:V${v}]-(re:Reaction)
  RETURN { id: $cid, name: cs.name, reactionCount: count(distinct(re)) } as data
  UNION
  MATCH (:Compartment {id: $cid})-[:V${v}]-(cm:CompartmentalizedMetabolite)
  RETURN { compartmentalizedMetaboliteCount: count(distinct cm) } as data
  UNION
  MATCH (:Compartment {id: $cid})-[:V${v}]-(:CompartmentalizedMetabolite)-[:V${v}]-(:Reaction)-[:V${v}]-(g:Gene)
  RETURN { geneCount: count(distinct g) } as data
  UNION
  MATCH (:Compartment {id: $cid})-[:V${v}]-(:CompartmentalizedMetabolite)-[:V${v}]-(:Reaction)-[:V${v}]-(:Subsystem)-[:V${v}]-(sss:SubsystemState)
  RETURN { majorSubsystems: COLLECT(DISTINCT(sss.name))[..15] } as data
", {cid:cid}) yield value
RETURN { compartment: apoc.map.mergeList(COLLECT(value.data)) } as xs

UNION

MATCH (rs:ReactionState)-[:V${v}]-(re:Reaction:${m})
WITH re, rs, rand() as r
ORDER BY r LIMIT 2
MATCH (re)-[:V${v}]-(cm:CompartmentalizedMetabolite)-[:V${v}]-(c:Compartment)
OPTIONAL MATCH (re)-[:V${v}]-(g:Gene)
OPTIONAL MATCH (re)-[:V${v}]-(s:Subsystem)
RETURN { reaction: { id: re.id, name: rs.name, equationWname: null, metaboliteCount: count(distinct cm), geneCount: count(distinct g), compartmentCount: count(distinct c), subsystemCount: count(distinct s) } } as xs

UNION

MATCH (:SubsystemState)-[:V${v}]-(s:Subsystem:${m})
WITH s.id as sid, rand() as r
ORDER BY r LIMIT 2
CALL apoc.cypher.run("
  MATCH (ss:SubsystemState)-[:V${v}]-(:Subsystem {id: $sid})-[:V${v}]-(re:Reaction)
  RETURN { id: $sid, name: ss.name, reactionCount: count(distinct(re)) } as data
  UNION
  MATCH (:Subsystem {id: $sid})-[:V${v}]-(:Reaction)-[:V${v}]-(cm:CompartmentalizedMetabolite)
  RETURN { id: $sid, compartmentalizedMetaboliteCount: count(distinct cm) } as data
  UNION
  MATCH (:Subsystem {id: $sid})-[:V${v}]-(:Reaction)-[:V${v}]-(g:Gene)
  RETURN { id: $sid, geneCount: count(distinct g) } as data
  UNION
  MATCH (:Subsystem {id: $sid})-[:V${v}]-(:Reaction)-[:V${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[:V${v}]-(c:Compartment)
  RETURN { id: $sid, compartmentCount: count(distinct c) } as data
", {sid:sid}) yield value
RETURN { subsystem: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as xs
`;

  const rows = await queryListResult(statement);
  return rows.reduce( (obj, row) => {
    const [componentType, component] = Object.entries(row)[0]

    if (componentType === "compartment") {
      obj[componentType] = component;
    } else {
      const key = `${componentType}s`;
      if (!obj[key]) {
        obj[key] = []
      }
      obj[key] = [...obj[key], component];
    }

    return obj;
  }, {});

};


export default getRandomComponents;
