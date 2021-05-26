import querySingleResult from 'neo4j/queryHandlers/single';
import parseParams from 'neo4j/shared/helper';

const getCompartment = async ({ id, model, version, full }) => {
  const [m, v] = parseParams(model, version);

  const statement = `
CALL apoc.cypher.run("
  MATCH (cs:CompartmentState)-[${v}]-(c:Compartment${m} {id: '${id}'})
  RETURN cs { id: c.id, .* } as data
  
  UNION
    
  MATCH (:Compartment${m} {id: '${id}'})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-(r:Reaction)-[${v}]-(s:Subsystem)-[${v}]-(ss:SubsystemState)
  USING JOIN on r
  RETURN { subsystems: COLLECT(DISTINCT({id: s.id, name: ss.name})) } as data
  
  UNION
  
  MATCH (:Compartment${m} {id: '${id}'})-[${v}]-(cm:CompartmentalizedMetabolite)-[${v}]-(r:Reaction)-[${v}]-(g:Gene)
  USING JOIN on r
  RETURN {
    reactionsCount: COUNT(DISTINCT(r)) ${ full ? ', reactions: COLLECT(DISTINCT(r))' : ''},
    metabolitesCount: COUNT(DISTINCT(cm)) ${ full ? ', metabolites: COLLECT(DISTINCT(cm))' : ''},
    genesCount: COUNT(DISTINCT(g)) ${ full ? ', genes: COLLECT(DISTINCT(g))' : ''}
  } as data
  
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
