import queryListResult from 'neo4j/queryHandlers/list';
import parseParams from 'neo4j/shared/helper';

const NODE_TYPES = {
  reaction: 'Reaction',
  gene: 'Gene',
  metabolite: 'Metabolite',
  subsystem: 'Subsystem',
  compartment: 'Compartment',
};

// TODO: add pagination and search
const getRelatedReactions = async ({ nodeType, id, model,  version, limit }) => {
  const [m, v] = parseParams(model, version);
  let statement;

  switch (nodeType) {
    case NODE_TYPES.reaction:
      statement = `
MATCH (r1:Reaction${m} {id: '${id}'})-[cms1${v}]-(:CompartmentalizedMetabolite)-[${v}]-(m:Metabolite)
WITH r1, count(cms1) as ccms1, collect(distinct(m)) as ms
UNWIND ms as m
MATCH (m)-[${v}]-(:CompartmentalizedMetabolite)-[cms2${v}]-(r:Reaction)
WITH r1, r, count(cms2) as ccms2, ccms1
WHERE ccms1 = ccms2
MATCH (r)-[cms3${v}]-(:CompartmentalizedMetabolite)
WITH ccms1, count(cms3) as ccms3, r1, r
WHERE ccms1 = ccms3 and r1.id <> r.id`;
      break;
    case NODE_TYPES.gene:
      statement = `
MATCH (:Gene${m} {id: '${id}'})-[${v}]-(r:Reaction)`;
      break;
    case NODE_TYPES.metabolite:
      statement = `
MATCH (:CompartmentalizedMetabolite${m} {id: '${id}'})-[${v}]-(r:Reaction)`;
      break;
    case NODE_TYPES.subsystem:
      statement = `
MATCH (:Subsystem${m} {id: '${id}'})-[${v}]-(r:Reaction)`;
      break;
    case NODE_TYPES.compartment:
      statement = `
MATCH (:Compartment${m} {id: '${id}'})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-(r:Reaction)`;
      break;
    default:
      throw new Error(`Unrecognized node type: ${nodeType}`);
  }

  statement += `
WITH r.id as rid
`;

  if (limit) {
    statement += `
LIMIT ${limit}
`;
  }

  statement += `
CALL apoc.cypher.run("
  MATCH (rs:ReactionState)-[${v}]-(:Reaction${m} {id: $rid})
  RETURN rs { id: $rid, .* } as data
 
  UNION
 
  MATCH (:Reaction${m} {id: $rid})-[${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm
  MATCH (cm)-[${v}]-(c:Compartment)-[${v}]-(cs:CompartmentState)
  USING JOIN on c
  RETURN { id: $rid, compartments: COLLECT(DISTINCT(cs {id: c.id, .*})) } as data
 
  UNION
 
  MATCH (:Reaction${m} {id: $rid})-[${v}]-(s:Subsystem)
  WITH DISTINCT s
  MATCH(s)-[${v}]-(ss:SubsystemState)
  RETURN { id: $rid, subsystems: COLLECT(DISTINCT(ss {id: s.id, .*})) } as data
 
  UNION
 
  MATCH (:Reaction${m} {id: $rid})-[${v}]-(g:Gene)
  WITH DISTINCT (g)
  MATCH (g)-[${v}]-(gs:GeneState)
  RETURN { id: $rid, genes: COLLECT(DISTINCT(gs {id: g.id, .*})) } as data
 
  UNION
 
  MATCH (:Reaction${m} {id: $rid})-[cmE${v}]-(cm:CompartmentalizedMetabolite)
  WITH DISTINCT cm, cmE
  MATCH (cm)-[${v}]-(c:Compartment)-[${v}]-(cs:CompartmentState)
  USING JOIN on c
  OPTIONAL MATCH (cm)-[${v}]-(:Metabolite)-[${v}]-(ms:MetaboliteState)
  RETURN { id: $rid, metabolites: COLLECT(DISTINCT(ms {id: cm.id, fullName: COALESCE(ms.name, '') + ' [' + COALESCE(cs.letterCode, '') + ']',  compartmentId: c.id, stoichiometry: cmE.stoichiometry, outgoing: startnode(cmE)=cm, .*})) } as data
", {rid:rid}) yield value
RETURN apoc.map.mergeList(apoc.coll.flatten(
    apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) as reactions
  ORDER BY reactions.id
`;

  return queryListResult(statement);
};


const getRelatedReactionsForReaction = ({ id, model, version, limit }) => getRelatedReactions({
  id, model, version, nodeType: NODE_TYPES.reaction, limit,
  });

const getRelatedReactionsForGene = ({ id, model, version, limit }) => getRelatedReactions({
  id, model, version, nodeType: NODE_TYPES.gene, limit,
  });

const getRelatedReactionsForMetabolite = ({ id, model, version, limit }) => getRelatedReactions({
  id, model, version, nodeType: NODE_TYPES.metabolite, limit,
  });

const getRelatedReactionsForSubsystem = ({ id, model, version, limit }) => getRelatedReactions({
  id, model, version, nodeType: NODE_TYPES.subsystem, limit,
  });

const getRelatedReactionsForCompartment = ({ id, model, version, limit }) => getRelatedReactions({
  id, model, version, nodeType: NODE_TYPES.compartment, limit,
  });

export {
  getRelatedReactionsForReaction,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForSubsystem,
  getRelatedReactionsForCompartment,
};
