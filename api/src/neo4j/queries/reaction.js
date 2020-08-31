import querySingleResult from 'neo4j/queryHandlers/single';
import reformatExternalDbs from 'neo4j/shared/formatter';

const getReaction = async ({ id, model, version }) => {
  const m = model ? `:${model}` : '';
  const v = version ? `:V${version}` : '';

  const statement = `
CALL apoc.cypher.run("
  MATCH (rs:ReactionState)-[${v}]-(r:Reaction${m} {id: '${id}'})
  RETURN rs { id: r.id, .* } as data
  
  UNION
  
  MATCH (r:Reaction${m} {id: '${id}'})-[${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[${v}]-(c:Compartment)-[${v}]-(cs:CompartmentState)
  RETURN { compartments: COLLECT(DISTINCT(cs {id: c.id, .*})) } as data
  
  UNION
  
  MATCH (r:Reaction${m} {id: '${id}'})-[${v}]-(s:Subsystem)-[${v}]-(ss:SubsystemState)
  RETURN { subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})) } as data
  
  UNION
  
  MATCH (r:Reaction${m} {id: '${id}'})-[${v}]-(g:Gene)-[${v}]-(gs:GeneState)
  RETURN { genes: COLLECT(DISTINCT(gs {id: g.id, .*})) } as data
  
  UNION
  
  MATCH (r:Reaction${m} {id: '${id}'})-[cmE${v}]-(cm:CompartmentalizedMetabolite)-[${v}]-(:Metabolite)-[${v}]-(ms:MetaboliteState)
  MATCH (cm)-[${v}]-(:Compartment)-[${v}]-(cs:CompartmentState)
  RETURN { metabolites: COLLECT(DISTINCT(ms {id: cm.id, compartment: cs.name, fullName: COALESCE(ms.name, '') + ' [' + COALESCE(cs.letterCode, '') + ']', stoichiometry: cmE.stoichiometry, outgoing: startnode(cmE)=cm, .*})) } as data
  
  UNION
  
  MATCH (r:Reaction${m} {id: '${id}'})-[${v}]-(e:ExternalDb)
  RETURN { externalDbs: COLLECT(DISTINCT(e {.*})) } as data
  
  UNION
  
  MATCH (r:Reaction${m} {id: '${id}'})-[${v}]-(p:PubmedReference)
  RETURN { pubmedIds: COLLECT(DISTINCT(p {.*})) } as data
  
  UNION
  
  MATCH (r:Reaction${m} {id: '${id}'})-[${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[${v}]-(:Compartment)-[${v}]-(csvg:SvgMap)
  RETURN { compartmentSVGs: COLLECT(DISTINCT(csvg {.*})) } as data
  
  UNION
  
  MATCH (r:Reaction${m} {id: '${id}'})-[${v}]-(:Subsystem)-[${v}]-(ssvg:SvgMap)
  RETURN { subsystemSVGs: COLLECT(DISTINCT(ssvg {.*})) } as data
", {}) yield value
RETURN apoc.map.mergeList(COLLECT(value.data)) as reaction
`;

  const reaction = await querySingleResult(statement);
  return { ...reaction, externalDbs: reformatExternalDbs(reaction.externalDbs) };
};

export default getReaction;
