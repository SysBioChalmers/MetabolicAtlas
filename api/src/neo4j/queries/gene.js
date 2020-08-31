import querySingleResult from 'neo4j/queryHandlers/single';
import reformatExternalDbs from 'neo4j/shared/formatter';

const getGene = async ({ id, model, version }) => {
  const m = model ? `:${model}` : '';
  const v = version ? `:V${version}` : '';

  const statement = `
CALL apoc.cypher.run("
  MATCH (gs:GeneState)-[${v}]-(g:Gene${m} {id: '${id}'})
  RETURN gs { id: g.id, .* } as data
  
  UNION
  
  MATCH (:Gene${m} {id: '${id}'})-[${v}]-(:Reaction)-[${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[${v}]-(c:Compartment)-[${v}]-(cs:CompartmentState)
  RETURN { compartments: COLLECT(DISTINCT({id: c.id, name: cs.name})) } as data
  
  UNION
  
  MATCH (:Gene${m} {id: '${id}'})-[${v}]-(:Reaction)-[${v}]-(s:Subsystem)-[${v}]-(ss:SubsystemState)
  RETURN { subsystems: COLLECT(DISTINCT({id: s.id, name: ss.name})) } as data
  
  UNION
  
  MATCH (:Gene${m} {id: '${id}'})-[${v}]-(e:ExternalDb)
  RETURN { externalDbs: COLLECT(DISTINCT(e {.*})) } as data
  
  UNION
  
  MATCH (:Gene${m} {id: '${id}'})-[${v}]-(:Reaction)-[${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[${v}]-(:Compartment)-[${v}]-(csvg:SvgMap)
  RETURN { compartmentSVGs: COLLECT(DISTINCT(csvg {.*})) } as data
  
  UNION
  
  MATCH (:Gene${m} {id: '${id}'})-[${v}]-(:Reaction)-[${v}]-(:Subsystem)-[${v}]-(ssvg:SvgMap)
  RETURN { subsystemSVGs: COLLECT(DISTINCT(ssvg {.*})) } as data
", {}) yield value
RETURN apoc.map.mergeList(COLLECT(value.data)) as gene
`;

  const gene = await querySingleResult(statement);
  return { ...gene, externalDbs: reformatExternalDbs(gene.externalDbs) };
};


export default getGene;
