import querySingleResult from 'neo4j/queryHandlers/single';
import parseParams from 'neo4j/shared/helper';
import populateWithLayout from 'utils/3d-network';

const get3dNetwork = async ({ model, version, type, id }) => {
  const [m, v] = parseParams(model, version);

  // compartment fragment
  const cf = type === 'compartment'
    ? `(:Compartment {id: "${id}"})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-`
    : '';

  // compartment fragment at end
  const cfe = type === 'compartment'
    ? `-[${v}]-(:Compartment {id: "${id}"})`
    : '';

  // subsystem fragment
  const sf = type === 'subsystem'
    ? `(s:Subsystem {id: "${id}"})-[${v}]-`
    : '';

  const f = `${cf}${sf}`;

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
  
  MATCH ${sf}(r:Reaction${m})-[cmE${v}]-(cm:CompartmentalizedMetabolite)${cfe}
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

  const network = await querySingleResult(statement);
  return populateWithLayout(network);
};

export default get3dNetwork;
