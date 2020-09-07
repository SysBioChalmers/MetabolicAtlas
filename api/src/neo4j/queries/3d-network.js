import querySingleResult from 'neo4j/queryHandlers/single';
import parseParams from 'neo4j/shared/helper';

const get3dNetwork = async ({ model, version, type, id }) => {
  const [m, v] = parseParams(model, version);

  const compartmentFragment = type === 'compartment'
    ? `(:Compartment {id: "${id}"})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-`
    : '';

  const subsystemFragment = type === 'subsystem'
    ? `(s:Subsystem {id: "${id}"})-[${v}]-`
    : '';

  const f = `${compartmentFragment}${subsystemFragment}`;

  const statement = `
CALL apoc.cypher.run('
  MATCH ${f}(r:Reaction${m})-[${v}]-(:ReactionState)
  RETURN {
    nodes: COLLECT(DISTINCT { g: "r", id: r.id, n: r.id })
  } as data
  
  UNION
  
  MATCH ${f}(r:Reaction${m})-[${v}]-(g:Gene)
  MATCH (g)-[${v}]-(gs:GeneState)
  RETURN {
    nodes: COLLECT(DISTINCT { g: "e", id: g.id, n: gs.name }),
    links: COLLECT(DISTINCT { s: g.id, t: r.id })
  } as data
  
  UNION
  
  MATCH ${f}(r:Reaction${m})-[cmE${v}]-(cm:CompartmentalizedMetabolite)
  MATCH (cm)-[${v}]-(:Metabolite)-[${v}]-(ms:MetaboliteState)
  RETURN {
    nodes: COLLECT(DISTINCT { g: "m", id: cm.id, n: ms.name }),
    links: COLLECT(DISTINCT(
      CASE
	WHEN startnode(cmE)=cm THEN { s: cm.id, t: r.id }
	ELSE { s: r.id, t: cm.id }
      END
    ))
  } as data
', {}) yield value
RETURN {
  nodes: apoc.coll.flatten(COLLECT(value.data.nodes)),
  links: apoc.coll.flatten(COLLECT(value.data.links))
}
`;

  return querySingleResult(statement);
};

export default get3dNetwork;
