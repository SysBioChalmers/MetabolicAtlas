import querySingleResult from 'neo4j/queryHandlers/single';
import { reformatExternalDbs } from 'neo4j/shared/formatter';
import parseParams from 'neo4j/shared/helper';

const getSubsystem = async ({ id, model, version }) => {
  const [m, v] = parseParams(model, version);

  const statement = `
CALL apoc.cypher.run("
  MATCH (ss:SubsystemState)-[${v}]-(s:Subsystem${m} {id: '${id}'})
  RETURN ss { id: s.id, .* } as data
  
  UNION
  
  MATCH (:Subsystem${m} {id: '${id}'})-[${v}]-(:Reaction)-[${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[${v}]-(c:Compartment)
  WITH DISTINCT c
  MATCH (c)-[${v}]-(cs:CompartmentState)
  RETURN { compartments: COLLECT({id: c.id, name: cs.name}) } as data
  
  UNION
  
  MATCH (:Subsystem${m} {id: '${id}'})-[${v}]-(:Reaction)-[${v}]-(g:Gene)
  WITH DISTINCT g
  MATCH (g)-[${v}]-(gs:GeneState)
  RETURN { genes: COLLECT({id: g.id, name: gs.name})[..1000] } as data
  
  UNION
  
  MATCH (:Subsystem${m} {id: '${id}'})-[${v}]-(e:ExternalDb)
  RETURN { externalDbs: COLLECT(DISTINCT(e {.*})) } as data
  
  UNION
  
  MATCH (:Subsystem${m} {id: '${id}'})-[${v}]-(:Reaction)-[${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[${v}]-(:Metabolite)-[${v}]-(ms:MetaboliteState)
  RETURN { metabolites: COLLECT(DISTINCT(ms {id: cm.id, name: ms.name}))[..1000] }  as data
  
  UNION
  
  MATCH (:Subsystem${m} {id: '${id}'})-[${v}]-(ssvg:SvgMap)
  WITH {subsystemId: '${id}', subsystemSVGs: COLLECT(DISTINCT(ssvg {.*}))} as subsystemSVG
  RETURN { subsystemSVGs: COLLECT(subsystemSVG) } as data
", {}) yield value
RETURN apoc.map.mergeList(COLLECT(value.data)) as subsystem
`;

  const result = await querySingleResult(statement);
  return { ...result, subsystemSVGs: [
    {
      id: result.id,
      customName: result.name,
      svgMaps: result.subsystemSVGs[0] ? result.subsystemSVGs[0].subsystemSVGs.sort((a, b) => a.id.localeCompare(b.id)) : [],
    }
  ], externalDbs: reformatExternalDbs(result.externalDbs) };
};


export default getSubsystem;
