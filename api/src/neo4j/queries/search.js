import queryListResult from 'neo4j/queryHandlers/list';
const INTEGRATED_MODELS = require('data/integratedModels');

const componentTypes = [
  "CompartmentalizedMetabolite",
  "Metabolite",
  "Gene",
  "Reaction",
  "Subsystem",
  "Compartment",
];

const intersect = (a, b) => [...new Set(a)].filter(x => new Set(b).has(x));

const fetchCompartmentalizedMetabolites = async ({ ids, model, version, limit, viaMetabolties }) => {
  if (!ids) {
    return null;
  }

  let statement = ``;

  if (viaMetabolties) {
    statement += `
WITH ${JSON.stringify(ids)} as mids
UNWIND mids as mid
MATCH (:Metabolite:${model} {id:mid})-[${version}]-(cm:CompartmentalizedMetabolite)
WITH DISTINCT(cm.id) as cmid
`;
  } else {
    statement += `
WITH ${JSON.stringify(ids)} as cmids
UNWIND cmids as cmid
`;
  }

  statement += `
CALL apoc.cypher.run('
  MATCH (ms:MetaboliteState)-[${version}]-(:Metabolite)-[${version}]-(:CompartmentalizedMetabolite:${model} {id: $cmid})
  RETURN ms { id: $cmid, .* } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite:${model} {id: $cmid})-[${version}]-(c:Compartment)-[${version}]-(cs:CompartmentState)
  RETURN { id: $cmid, compartment: cs { id: c.id, .* } } as data
  
  UNION
  
  MATCH (:CompartmentalizedMetabolite:${model} {id: $cmid})-[${version}]-(:Reaction)-[${version}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH (s)-[${version}]-(ss:SubsystemState)
  RETURN { id: $cmid, subsystem: COLLECT({id: s.id, name: ss.name}) } as data
', {cmid:cmid}) yield value
RETURN apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as metabolites
`;

  if (limit) {
    statement += `
LIMIT ${limit}
`;
  }

  return queryListResult(statement);
};


const fetchGenes = async ({ ids, model, version }) => {
  if (!ids) {
    return null;
  }

  const statement = `
WITH ${JSON.stringify(ids)} as gids
UNWIND gids as gid
CALL apoc.cypher.run("
  MATCH (gs:GeneState)-[${version}]-(:Gene:${model} {id: $gid})
  RETURN { id: $gid, name: gs.name } as data
  
  UNION
  
  MATCH (:Gene:${model} {id: $gid})-[${version}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[${version}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH (s)-[${version}]-(ss:SubsystemState)
  RETURN { id: $gid, subsystem: COLLECT({ id: s.id, name: ss.name }) } as data
  
  UNION
  
  MATCH (:Gene:${model} {id: $gid})-[${version}]-(:Reaction)-[${version}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[${version}]-(c:Compartment)-[${version}]-(cs:CompartmentState)
  USING JOIN on c
  RETURN { id: $gid, compartment: COLLECT(DISTINCT({ id: c.id, name: cs.name })) } as data
", {gid:gid}) yield value
RETURN apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as gene
`;

  return queryListResult(statement);
};


const fetchReactions = async ({ ids, model, version, includeMetabolites }) => {
  if (!ids) {
    return null;
  }

  let statement = `
WITH ${JSON.stringify(ids)} as rids
UNWIND rids as rid
CALL apoc.cypher.run("
  MATCH (rs:ReactionState)-[${version}]-(:Reaction:${model} {id: $rid})
  RETURN rs { id: $rid, .* } as data
`;

  if (includeMetabolites) {
    statement += `
  UNION
  
  MATCH (r:Reaction:${model} {id: $rid})-[cmE${version}]-(cm:CompartmentalizedMetabolite)-[${version}]-(:Metabolite)-[${version}]-(ms:MetaboliteState)
  MATCH (cm)-[${version}]-(c:Compartment)-[${version}]-(cs:CompartmentState)
  USING JOIN on c
  RETURN { id: $rid, metabolites: COLLECT(DISTINCT(ms {id: cm.id, compartment: cs.name, fullName: COALESCE(ms.name, '') + ' [' + COALESCE(cs.letterCode, '') + ']', stoichiometry: cmE.stoichiometry, outgoing: startnode(cmE)=cm, .*})) } as data
`;
  }

  statement += `
  UNION
  
  MATCH (:Reaction:${model} {id: $rid})-[${version}]-(s:Subsystem)-[${version}]-(ss:SubsystemState)
  USING JOIN on s
  RETURN { id: $rid, subsystem: COLLECT(DISTINCT({ id: s.id, name: ss.name })) } as data
  
  UNION
  
  MATCH (:Reaction:${model} {id: $rid})-[${version}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[${version}]-(c:Compartment)-[${version}]-(cs:CompartmentState)
  USING JOIN on c
  RETURN { id: $rid, compartment: COLLECT(DISTINCT({ id: c.id, name: cs.name })) } as data
", {rid:rid}) yield value
RETURN apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as reaction
`;

  return queryListResult(statement);
};

const fetchSubsystems = async ({ ids, model, version, includeCounts }) => {
  if (!ids) {
    return null;
  }

  let statement = `
WITH ${JSON.stringify(ids)} as sids
UNWIND sids as sid
CALL apoc.cypher.run("
  MATCH (ss:SubsystemState)-[${version}]-(:Subsystem:${model} {id: $sid})
  RETURN { id: $sid, name: ss.name } as data
`;

  if (includeCounts) {
    statement += ` 
  UNION
  
  MATCH (:Subsystem:${model} {id: $sid})-[${version}]-(r:Reaction)
  RETURN { id: $sid, reactionCount: COUNT(DISTINCT(r)) } as data
  
  UNION
  
  MATCH (:Subsystem:${model} {id: $sid})-[${version}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[${version}]-(cm:CompartmentalizedMetabolite)
  RETURN { id: $sid, compartmentalizedMetaboliteCount: COUNT(DISTINCT cm) } as data
  
  UNION
  
  MATCH (:Subsystem:${model} {id: $sid})-[${version}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[${version}]-(g:Gene)
  RETURN { id: $sid, geneCount: COUNT(DISTINCT g) } as data
`;
  }

  statement += ` 
  UNION
  
  MATCH (:Subsystem:${model} {id: $sid})-[${version}]-(:Reaction)-[${version}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[${version}]-(c:Compartment)-[${version}]-(cs:CompartmentState)
  USING JOIN on c
  RETURN { id: $sid, compartment: COLLECT(DISTINCT({ id: c.id, name: cs.name })) } as data
", {sid:sid}) yield value
RETURN apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as subsystem
`;

  return queryListResult(statement);
};

const fetchCompartments = async ({ ids, model, version, includeCounts }) => {
  if (!ids) {
    return null;
  }

  let statement = `
WITH ${JSON.stringify(ids)} as cids
UNWIND cids as cid
CALL apoc.cypher.run("
  MATCH (cs:CompartmentState)-[${version}]-(:Compartment:${model} {id: $cid})
  RETURN cs { id: $cid, .* } as data
`;

  if (includeCounts) {
    statement += ` 
  UNION
  
  MATCH (:Compartment:${model} {id: $cid})-[${version}]-(:CompartmentalizedMetabolite)-[${version}]-(r:Reaction)
  RETURN { id: $cid, reactionCount: COUNT(DISTINCT(r)) } as data
  
  UNION
  
  MATCH (:Compartment:${model} {id: $cid})-[${version}]-(cm:CompartmentalizedMetabolite)
  RETURN { id: $cid, compartmentalizedMetaboliteCount: COUNT(DISTINCT cm) } as data
  
  UNION
  
  MATCH (:Compartment:${model} {id: $cid})-[${version}]-(:CompartmentalizedMetabolite)-[${version}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[${version}]-(g:Gene)
  RETURN { id: $cid, geneCount: COUNT(DISTINCT g) } as data
  
  UNION
  
  MATCH (:Compartment:${model} {id: $cid})-[${version}]-(:CompartmentalizedMetabolite)-[${version}]-(r:Reaction)
  WITH DISTINCT r
  MATCH (r)-[${version}]-(s:Subsystem)
  RETURN { id: $cid, subsystemCount: COUNT(DISTINCT s) } as data
`;
  }

  statement += ` 
", {cid:cid}) yield value
RETURN apoc.map.mergeList(apoc.coll.flatten(
	apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as compartment
`;

  return queryListResult(statement);
};

const MODELS = INTEGRATED_MODELS.map(m => ({ label: m.short_name.replace('-GEM', 'Gem'), name: m.short_name }));

const globalSearch = async ({ searchTerm, version, limit }) => {
  const results = await Promise.all(MODELS.map(m =>
    _search({ searchTerm, version, model: m.label, limit, includeCounts: true })
  ));

  return MODELS.reduce((obj, m, i) => {
    obj[m.name] = {
      ...results[i],
      name: m.name,
    };
    return obj;
  }, {});
};

const modelSearch = async ({ searchTerm, model, version, limit }) => {
  const match = MODELS.filter(m => m.label == model);
  if (match.length === 0) {
    throw new Error(`Invalid model: ${model}`);
  }
  
  const results = await _search({ searchTerm, model, version, limit: limit || 50 });

  return {
    [match[0].name]: {
      ...results,
      name: match[0].name,
      metabolite: results.metabolite.map(m => ({ ...m, compartment: m.compartment.name })),
    }
  };
};

/*
 * The search consists of two steps
 * 1. Do a fuzzy search over all nodes covered by full-text search index
 * 2. Fetch results for each component type (parallelly) and return result
 */
const _search = async ({ searchTerm, model, version, limit, includeCounts }) => {
  const v = version ? `:V${version}` : '';

  // the EC field for reaction could contain ":", which is a special character
  // in this case th search term is modified to be escape and perform an exact match
  const term = searchTerm.includes("EC:") ? `\\"${searchTerm}~\\"` : `${searchTerm}~`;

  // Metabolites are not included as it would mess with the limit and
  // relevant metabolites should be matched through CompartmentalizedMetabolites
  let statement = `
CALL db.index.fulltext.queryNodes("fulltext", "${term}")
YIELD node, score
WITH node, score, LABELS(node) as labelList
OPTIONAL MATCH (node)-[${v}]-(parentNode:${model})
WHERE node:${model} OR parentNode:${model}
WITH DISTINCT(
	CASE
		WHEN EXISTS(node.id) THEN { id: node.id, labels: labelList, score: score }
		ELSE { id: parentNode.id, labels: LABELS(parentNode), score: score }
	END
) as r 
WHERE any(r IN r.labels WHERE r="${model}")
RETURN r
`;
  if (limit) {
    statement += `
LIMIT ${limit}
`;
  }

  const results = await queryListResult(statement);

  const uniqueIds = results.reduce((o, r) => {
    const c = intersect(componentTypes, r.labels);
    if (!o[c]) {
      o[c] = new Set();
    }
    o[c].add(r.id);
    return o;
  }, {});

  const ids = Object.assign({}, ...Object.keys(uniqueIds).map(c => ({ [c]: Array.from(uniqueIds[c]) })));

  const [
    compartmentalizedMetabolites,
    metabolites,
    genes,
    reactions,
    subsystems,
    compartments,
  ] = await Promise.all([
    fetchCompartmentalizedMetabolites({ ids: ids["CompartmentalizedMetabolite"], model, version: v, limit }),
    fetchCompartmentalizedMetabolites({ ids: ids["Metabolite"], model, version: v, limit, viaMetabolties: true }),
    fetchGenes({ ids: ids["Gene"], model, version: v }),
    fetchReactions({ ids: ids["Reaction"], model, version: v, includeMetabolites: !!limit }),
    fetchSubsystems({ ids: ids["Subsystem"], model, version: v, includeCounts: true }),
    fetchCompartments({ ids: ids["Compartment"], model, version: v, includeCounts: true }),
  ]);

  // formatting for simple (gem browser) search
  return {
    metabolite: [...compartmentalizedMetabolites || [], ...metabolites || []],
    gene: genes || [],
    reaction: reactions || [],
    subsystem: subsystems || [],
    compartment: compartments || [],
  };
};

const search = async (params) => params.model ? modelSearch(params) : globalSearch(params);

export { search };
