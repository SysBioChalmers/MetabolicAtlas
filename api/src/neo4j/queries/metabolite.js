import querySingleResult from 'neo4j/queryHandlers/single';
import reformatExternalDbs from 'neo4j/shared/formatter';
import parseParams from 'neo4j/shared/helper';

const getMetabolite = async ({ id, model, version }) => {
  const [m, v] = parseParams(model, version);

  const statement = `
CALL apoc.cypher.run('
  MATCH (ms:MetaboliteState)-[${v}]-(:Metabolite)-[${v}]-(cm:CompartmentalizedMetabolite${m} {id: "${id}"})
  RETURN ms { id: cm.id, .* } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite${m} {id: "${id}"})-[${v}]-(c:Compartment)-[${v}]-(cs:CompartmentState)
  RETURN { compartment: cs { id: c.id, .* } } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite${m} {id: "${id}"})-[${v}]-(:Compartment)-[${v}]-(csvg:SvgMap)
  RETURN { compartmentSVGs: COLLECT(DISTINCT(csvg {.*})) } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite${m} {id: "${id}"})-[${v}]-(:Reaction)-[${v}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH (s)-[${v}]-(ss:SubsystemState)
  RETURN { subsystems: COLLECT(DISTINCT({id: s.id, name: ss.name})) } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite${m} {id: "${id}"})-[${v}]-(e:ExternalDb)
  RETURN { externalDbs: COLLECT(e {.*}) } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite${m} {id: "${id}"})-[${v}]-(:Reaction)-[${v}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH (s)-[${v}]-(ssvg:SvgMap)
  RETURN { subsystemSVGs: COLLECT(DISTINCT(ssvg {.*})) } as data
', {}) yield value
RETURN apoc.map.mergeList(COLLECT(value.data)) as metabolite
`;
  const metabolite = await querySingleResult(statement);
  return { ...metabolite, externalDbs: reformatExternalDbs(metabolite.externalDbs) };
};


export default getMetabolite;
