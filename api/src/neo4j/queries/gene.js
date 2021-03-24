import querySingleResult from 'neo4j/queryHandlers/single';
import queryListResult from 'neo4j/queryHandlers/list';
import reformatExternalDbs from 'neo4j/shared/formatter';
import parseParams from 'neo4j/shared/helper';

const getGene = async ({ id, model, version }) => {
  const [m, v] = parseParams(model, version);

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

const getGenesForHPA = async () => {
  const statement = `
MATCH (g:Gene:HumanGem)-[:V1_3_0]-(:Reaction)-[:V1_3_0]-(s:Subsystem)-[:V1_3_0]-(ss:SubsystemState)
RETURN DISTINCT [g.id, ss.name, s.id]
`;

  return queryListResult(statement);
};

const getGeneDetailsForHPA = async ({ id }) => {
  const statement = `
MATCH (g:Gene:HumanGem {id:'${id}'})-[:V1_3_0]-(:Reaction)-[:V1_3_0]-(s:Subsystem)-[:V1_3_0]-(ss:SubsystemState)
RETURN DISTINCT { id: s.id, name: ss.name }
`;

  const result = await queryListResult(statement);

  const subsystems = result.map(({ id, name }) => ({
    name,
    subsystem_url: `https://metabolicatlas.org/explore/Human-GEM/gem-browser/subsystem/${id}`,
  }));

  return {
    gene_url: `https://metabolicatlas.org/explore/Human-GEM/gem-browser/gene/${id}`, 
    subsystems,
    doc: 'A subsystem can contain the same chemical metabolite that comes from different compartments.',
  };
};

export { getGene, getGenesForHPA, getGeneDetailsForHPA };
