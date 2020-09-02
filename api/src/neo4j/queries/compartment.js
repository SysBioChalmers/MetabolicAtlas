import querySingleResult from 'neo4j/queryHandlers/single';
import parseParams from 'neo4j/shared/helper';

const getCompartment = async ({ id, model, version, full }) => {
  const [m, v] = parseParams(model, version);

  const statement = `
CALL apoc.cypher.run("
  MATCH (cs:CompartmentState)-[${v}]-(c:Compartment${m} {id: '${id}'})
  RETURN cs { id: c.id, .* } as data
  
  UNION
    
  MATCH (:Compartment${m} {id: '${id}'})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-(:Reaction)-[${v}]-(s:Subsystem)-[${v}]-(ss:SubsystemState)
  RETURN { subsystems: COLLECT(DISTINCT({id: s.id, name: ss.name})) } as data
  
  UNION
  
  MATCH (:Compartment${m} {id: '${id}'})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-(r:Reaction)
  RETURN { reactionsCount: COUNT(DISTINCT(r)) ${ full ? ', reactions: COLLECT(DISTINCT(r.id))' : ''}} as data
  
  UNION
  
  MATCH (:Compartment${m} {id: '${id}'})-[${v}]-(cm:CompartmentalizedMetabolite)
  RETURN { metabolitesCount: COUNT(DISTINCT(cm)) ${ full ? ', metabolites: COLLECT(DISTINCT(cm.id))' : ''}} as data
  
  UNION
  
  MATCH (:Compartment${m} {id: '${id}'})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-(:Reaction)-[${v}]-(g:Gene)
  RETURN { genesCount: COUNT(DISTINCT(g)) ${ full ? ', genes: COLLECT(DISTINCT(g.id))' : ''}} as data
  
  UNION
  
  MATCH (:Compartment${m} {id: '${id}'})-[${v}]-(e:ExternalDb)
  RETURN { externalDbs: COLLECT(DISTINCT(e {.*})) } as data
  
  UNION
  
  MATCH (:Compartment${m} {id: '${id}'})-[${v}]-(csvg:SvgMap)
  RETURN { compartmentSVGs: COLLECT(DISTINCT(csvg {.*})) } as data
", {}) yield value
RETURN apoc.map.mergeList(COLLECT(value.data)) as compartment
`;

  const { subsystems, compartmentSVGs, externalDbs, ...info } = await querySingleResult(statement);
  return {
    info: {
      ...info,
      subsystemCount: subsystems.length,
    },
    compartmentSVGs,
    externalDbs,
    subsystems,
  };

};


export default getCompartment;
