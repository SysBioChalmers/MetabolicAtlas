import queryListResult from 'neo4j/queryHandlers/list';
import reformatExternalDbs from 'neo4j/shared/formatter';
import parseParams from 'neo4j/shared/helper';

const getRandomComponents = async ({ model, version, componentTypes = {
  compartment: true,
  compartmentalizedMetabolite: true,
  gene: true,
  reaction: true,
  subsystem: true,
}}) => {
  if (Object.values(componentTypes).filter(v => v === true).length === 0) {
    throw new Error ('At least 1 component type is needed');
  }

  const [m, v] = parseParams(model, version);
  const { compartment, compartmentalizedMetabolite, gene, reaction, subsystem } = componentTypes;

  let statement = '';

  if (gene) {
    statement += `
MATCH (:GeneState)-[${v}]-(g:Gene${m})
WITH g.id as gid, rand() as r
ORDER BY r LIMIT 2
CALL apoc.cypher.run("
  MATCH (gs:GeneState)-[${v}]-(:Gene${m} {id: $gid})-[${v}]-(re:Reaction)
  RETURN { id: $gid, name: gs.name, reactionCount: COUNT(DISTINCT(re)) } as data
  UNION
  MATCH (:Gene${m} {id: $gid})-[${v}]-(:Reaction)-[${v}]-(ss:Subsystem)
  RETURN { id: $gid, subsystemCount: COUNT(DISTINCT(ss)) } as data
  UNION
  MATCH (:Gene${m} {id: $gid})-[${v}]-(:Reaction)-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-(c:Compartment)
  RETURN { id: $gid, compartmentCount: COUNT(DISTINCT(c)) } as data
", {gid:gid}) yield value
RETURN { gene: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as xs
`;
  }

  if (compartmentalizedMetabolite) {
    if (statement.length > 0) {
      statement += `
UNION`;
    }

    statement += `
MATCH (:Metabolite)-[${v}]-(cm:CompartmentalizedMetabolite${m})
WITH cm.id as cmid, rand() as r
ORDER BY r LIMIT 2
CALL apoc.cypher.run("
  MATCH (ms:MetaboliteState)-[${v}]-(:Metabolite)-[${v}]-(:CompartmentalizedMetabolite${m} {id: $cmid})
  RETURN { id: $cmid, name: ms.name, formula: ms.formula } as data
  UNION
  MATCH (re:Reaction)-[${v}]-(:CompartmentalizedMetabolite${m} {id: $cmid})
  RETURN { id: $cmid, reactionCount: count(distinct(re)) } as data
  UNION
  MATCH (cs:CompartmentState)-[${v}]-(:Compartment)-[${v}]-(cm:CompartmentalizedMetabolite${m} {id: $cmid})
  RETURN { id: $cmid, compartment: cs.name } as data
", {cmid:cmid}) yield value
RETURN { metabolite: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as xs
`;
  }

  if (compartment) {
    if (statement.length > 0) {
      statement += `
UNION`;
    }

    statement += `
MATCH (:CompartmentState)-[${v}]-(c:Compartment${m})
WITH c.id as cid, rand() as r
ORDER BY r LIMIT 1
CALL apoc.cypher.run("
  MATCH (cs:CompartmentState)-[${v}]-(:Compartment${m} {id: $cid})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-(re:Reaction)
  RETURN { id: $cid, name: cs.name, reactionCount: count(distinct(re)) } as data
  UNION
  MATCH (:Compartment${m} {id: $cid})-[${v}]-(cm:CompartmentalizedMetabolite)
  RETURN { compartmentalizedMetaboliteCount: count(distinct cm) } as data
  UNION
  MATCH (:Compartment${m} {id: $cid})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-(:Reaction)-[${v}]-(g:Gene)
  RETURN { geneCount: count(distinct g) } as data
  UNION
  MATCH (:Compartment${m} {id: $cid})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-(:Reaction)-[${v}]-(s:Subsystem)-[${v}]-(sss:SubsystemState)
  USING JOIN on s
  RETURN { majorSubsystems: COLLECT(DISTINCT(sss.name))[..15] } as data
", {cid:cid}) yield value
RETURN { compartment: apoc.map.mergeList(COLLECT(value.data)) } as xs
`;
  }

  if (reaction) {
    if (statement.length > 0) {
      statement += `
UNION`;
    }
    statement += `
MATCH (rs:ReactionState)-[${v}]-(re:Reaction${m})
WITH re, rs, rand() as r
ORDER BY r LIMIT 2
MATCH (re)-[${v}*2]-(c:Compartment)
WITH re, rs, collect(distinct c) as comps
OPTIONAL MATCH (re)<-[${v}]-(:CompartmentalizedMetabolite)-[${v}*2]-(ms:MetaboliteState)
WITH re, rs, comps, collect(ms.name) as reactants
OPTIONAL MATCH (re)-[${v}]->(:CompartmentalizedMetabolite)-[${v}*2]-(ms:MetaboliteState)
WITH re, rs, comps, reactants, collect(ms.name) as products
OPTIONAL MATCH (re)-[${v}]-(g:Gene)
WITH re, rs, reactants, products, comps, count(g) as geneCount
OPTIONAL MATCH (re)-[${v}]-(s:Subsystem)
RETURN { reaction: { id: re.id, name: rs.name, reactants: reactants, products: products, geneCount: geneCount, compartmentCount: size(comps), subsystemCount: count(s) }, reversible: rs.reversible } as xs
`;
  }

  if (subsystem) {
    if (statement.length > 0) {
      statement += `
UNION`;
    }
    statement += `
MATCH (:SubsystemState)-[${v}]-(s:Subsystem${m})
WITH s.id as sid, rand() as r
ORDER BY r LIMIT 2
CALL apoc.cypher.run("
  MATCH (ss:SubsystemState)-[${v}]-(:Subsystem${m} {id: $sid})-[${v}]-(re:Reaction)
  RETURN { id: $sid, name: ss.name, reactionCount: count(distinct(re)) } as data
  UNION
  MATCH (:Subsystem${m} {id: $sid})-[${v}]-(:Reaction)-[${v}]-(cm:CompartmentalizedMetabolite)
  RETURN { id: $sid, compartmentalizedMetaboliteCount: count(distinct cm) } as data
  UNION
  MATCH (:Subsystem${m} {id: $sid})-[${v}]-(:Reaction)-[${v}]-(g:Gene)
  RETURN { id: $sid, geneCount: count(distinct g) } as data
  UNION
  MATCH (:Subsystem${m} {id: $sid})-[${v}]-(:Reaction)-[${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[${v}]-(c:Compartment)
  RETURN { id: $sid, compartmentCount: count(distinct c) } as data
", {sid:sid}) yield value
RETURN { subsystem: apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as xs
`;
  }

  const rows = await queryListResult(statement);
  return rows.reduce((obj, row) => {
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
