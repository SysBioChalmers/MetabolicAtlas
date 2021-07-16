import querySingleResult from 'neo4j/queryHandlers/single';
import queryListResult from 'neo4j/queryHandlers/list';
import { reformatExternalDbs, reformatCompartmentSVGs, reformatSubsystemSVGs } from 'neo4j/shared/formatter';
import parseParams from 'neo4j/shared/helper';
import integratedGemsRepoJson from 'data/integratedModels.json';

const BASE_URL = 'https://metabolicatlas.org';

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
  MATCH (cm)-[${v}]-(c:Compartment)-[${v}]-(csvg:SvgMap)
  WITH {compartmentId: c.id, compartmentSVGs: COLLECT(DISTINCT(csvg {.*}))} as compartmentSVG
  RETURN { compartmentSVGs: COLLECT(compartmentSVG) } as data
  
  UNION
  
  MATCH (:Gene${m} {id: '${id}'})-[${v}]-(:Reaction)-[${v}]-(s:Subsystem)-[${v}]-(ssvg:SvgMap)
  WITH {subsystemId: s.id, subsystemSVGs: COLLECT(DISTINCT(ssvg {.*}))} as subsystemSVG
  RETURN { subsystemSVGs: COLLECT(subsystemSVG) } as data
", {}) yield value
RETURN apoc.map.mergeList(COLLECT(value.data)) as gene
`;

  const gene = await querySingleResult(statement);
  return { ...gene, compartmentSVGs: reformatCompartmentSVGs(gene), subsystemSVGs: reformatSubsystemSVGs(gene), externalDbs: reformatExternalDbs(gene.externalDbs) };
};

const getHumanLabelAndVersion = () => {
  const humanGem = integratedGemsRepoJson.find(g => g.short_name === 'Human-GEM'); 
  const label = `:${humanGem.short_name.split('-').map(s => s[0] + s.slice(1).toLowerCase()).join('')}`;
  const version = `:V${humanGem.version.split('.').join('_')}`;
  return [label, version];
};


const getGenesForHPA = async () => {
  const [l, v] = getHumanLabelAndVersion();

  const statement = `
MATCH (g:Gene${l})-[${v}]-(r:Reaction)-[${v}]-(s:Subsystem)-[${v}]-(ss:SubsystemState)
USING JOIN ON r
RETURN DISTINCT [g.id, ss.name, s.id]
`;

  return queryListResult(statement);
};


const getGeneDetailsForHPA = async ({ id }) => {
  const [l, v] = getHumanLabelAndVersion();

  const subsystemsStatement = `
MATCH (:Gene${l} {id:'${id}'})-[${v}]-(r:Reaction)-[${v}]-(s:Subsystem)-[${v}]-(ss:SubsystemState)
WITH DISTINCT s.id as sids, COLLECT(r.id) as rids, ss
UNWIND sids as sid
CALL apoc.cypher.run("
  MATCH (:Subsystem {id: $sid})-[${v}]-(r:Reaction)-[${v}]-(cm:CompartmentalizedMetabolite)
  USING JOIN ON r
  WITH DISTINCT cm
  MATCH (m:Metabolite)-[${v}]-(cm)-[${v}]-(c:Compartment)-[${v}]-(cs:CompartmentState)
  USING JOIN ON c
  RETURN DISTINCT { id: $sid, compartments: COLLECT(DISTINCT(cs.name)), model_metabolite_count: COUNT(DISTINCT(m)), compartment_metabolite_count: COUNT(cm) } as data

  UNION

  MATCH (:Subsystem {id: $sid})-[${v}]-(r:Reaction)-[${v}]-(g:Gene)
  USING JOIN ON r
  RETURN DISTINCT { id: $sid, genes: COLLECT(DISTINCT(g.id)) } as data

  UNION

  MATCH (:Subsystem {id: $sid})-[${v}]-(r:Reaction)
  RETURN DISTINCT { id: $sid, reaction_count: COUNT(DISTINCT(r)) } as data

  UNION

  MATCH (:Subsystem {id: $sid})-[${v}]-(r:Reaction)
  WHERE r.id IN $rids
  RETURN DISTINCT { id: $sid, reactions_catalysed: COUNT(DISTINCT(r)) } as data

  UNION

  MATCH (:Subsystem {id: $sid})-[${v}]-(ssvg:SvgMap)
  RETURN { id: $sid,  svgs: COLLECT(ssvg.filename) } as data
", { sid: sid, rids: rids }) yield value
RETURN DISTINCT {
  id: sid,
  name: ss.name,
  details: apoc.map.mergeList(apoc.coll.flatten(
    apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
  ))
}
`;

  const compartmentsStatement = `
MATCH (:Gene${l} {id: '${id}'})-[${v}]-(:Reaction)-[${v}]-(cm:CompartmentalizedMetabolite)
WITH DISTINCT cm
MATCH (cm)-[${v}]-(c:Compartment)-[${v}]-(cs:CompartmentState)
RETURN DISTINCT({id: c.id, name: cs.name})
`;

  const [subsystemsResult, compartmentsResult] = await Promise.all(
    [queryListResult(subsystemsStatement), queryListResult(compartmentsStatement)]
  );
  
  const subsystems = subsystemsResult.map(({
    id,
    name,
    details: {
      compartments,
      genes,
      reactions_catalysed,
      model_metabolite_count,
      compartment_metabolite_count,
      reaction_count,
      svgs
    }
  }) => ({
    name,
    compartments,
    genes,
    reactions_catalysed,
    map_url: `${BASE_URL}/api/v2/svg/Human-GEM/${svgs[0]}`,
    subsystem_url: `${BASE_URL}/explore/Human-GEM/gem-browser/subsystem/${id}`,
    model_metabolite_count,
    compartment_metabolite_count,
    reaction_count,
    gene_count: genes.length
  }));

  const compartments = compartmentsResult.map(({id, name}) => ({
    name,
    compartment_url: `${BASE_URL}/explore/Human-GEM/gem-browser/compartment/${id}`,
  }));

  return {
    gene_url: `${BASE_URL}/explore/Human-GEM/gem-browser/gene/${id}`, 
    compartments,
    subsystems,
    doc: 'A subsystem can contain the same chemical metabolite that comes from different compartments.',
  };
};

export { getGene, getGenesForHPA, getGeneDetailsForHPA };
