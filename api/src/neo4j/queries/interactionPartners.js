import querySingleResult from 'neo4j/queryHandlers/single';
import parseParams from 'neo4j/shared/helper';

const getInteractionPartners = async ({ id, model, version }) => {
  const [m, v] = parseParams(model, version);

  const statement = `
MATCH (comp${m} {id: "${id}"})
WHERE comp:Gene OR comp:CompartmentalizedMetabolite

WITH CASE WHEN comp:Gene THEN 'gene' ELSE 'metabolite' END AS compType, comp

CALL apoc.when(
  comp:Gene,
  'MATCH (g:Gene${m} {id: comp.id})-[${v}]-(gs:GeneState)'
  +	'RETURN {id: g.id, name: gs.name, type: compType} as component',
  'MATCH (cm:CompartmentalizedMetabolite${m} {id: comp.id})-[${v}]-(:Metabolite)-[${v}]-(ms:MetaboliteState)'
  + ' RETURN {id: cm.id, name: ms.name, type: compType} as component',
  {comp:comp, compType:compType})
YIELD value as v

WITH v.component as component
MATCH (${m} {id: component.id})-[${v}]-(r:Reaction)

CALL apoc.cypher.run("
  MATCH (:Reaction${m} {id: $rid})-[${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[${v}]-(c:Compartment)-[${v}]-(cs:CompartmentState)
  RETURN { id: $rid, compartments: COLLECT(DISTINCT({ id: c.id, name: cs.name })) } as data
 
  UNION
 
  MATCH (:Reaction${m} {id: $rid})-[${v}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH(s)-[${v}]-(ss:SubsystemState)
  RETURN { id: $rid, subsystem: COLLECT(ss.name) } as data
 
  UNION
 
  MATCH (:Reaction${m} {id: $rid})-[${v}]-(g:Gene)
  WITH DISTINCT (g)
  MATCH (g)-[${v}]-(gs:GeneState)
  RETURN { id: $rid, genes: COLLECT(DISTINCT(gs {id: g.id, .*})) } as data
 
  UNION
 
  MATCH (:Reaction${m} {id: $rid})-[cmE${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm, cmE
  MATCH (c:Compartment)-[${v}]-(cm)-[${v}]-(:Metabolite)-[${v}]-(ms:MetaboliteState)
  RETURN { id: $rid, metabolites: COLLECT(DISTINCT({id: cm.id, name: ms.name,  compartmentId: c.id, outgoing: startnode(cmE)=cm})) } as data

", {rid:r.id}) yield value
WITH apoc.map.mergeList(apoc.coll.flatten(
    apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as reaction, component
RETURN { component: component, reactions: COLLECT(reaction) }
`;

  return querySingleResult(statement);
};


export default getInteractionPartners;
