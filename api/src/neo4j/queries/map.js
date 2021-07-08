import querySingleResult from 'neo4j/queryHandlers/single';
import queryListResult from 'neo4j/queryHandlers/list';
import parseParams from 'neo4j/shared/helper';
import fs from 'fs';
import readline from 'readline';

const mapReactionIdSet = async (map, modelShortName) => {
  const rl = readline.createInterface({
      input: fs.createReadStream(`/project/svg/${modelShortName}/${map.filename}`),
      output: process.stdout,
      terminal: false
  });

  const mapReactionIdSet = new Set();
  const getReactions = async () =>{
    for await (const line of rl) {
      if (line.includes('class="rea"')) {
        const match = line.match(/id="(.+)"\s/);
        if (match) {
          mapReactionIdSet.add(match[1]);
        }
      }
    }
  }
  await getReactions()
  return {...map, mapReactionIdSet: [...mapReactionIdSet]}
};

const mapComponents = async (componentList, modelShortName) =>
  await Promise.all(componentList.map(async (component) => {
    const svgs = await Promise.all(component.svgs.map((map) => {
      return mapReactionIdSet(map, modelShortName);
    }));
    return { ...component, svgs };
  }));

const getMapsListing = async ({ model, version }) => {
  const [m, v] = parseParams(model, version);

  const componentSvgsQuery = `
MATCH (:CompartmentState)-[${v}]-(c:Compartment${m})
CALL apoc.cypher.run("
  MATCH (cs:CompartmentState)-[${v}]-(:Compartment${m} {id: $cid})
  RETURN cs { id: $cid, .* } as data
  
  UNION
  
  MATCH (:Compartment${m} {id: $cid})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-(r:Reaction)
  RETURN { id: $cid, reactionCount: COUNT(DISTINCT(r)) } as data
  
  UNION

  MATCH (:Compartment${m} {id: $cid})-[${v}]-(:CompartmentalizedMetabolite)-[${v}]-(r:Reaction)
  RETURN { id: $cid, reactionList: COLLECT(DISTINCT(r.id)) } as data
  
  UNION
  
  MATCH (csvg:SvgMap)-[${v}]-(:Compartment${m} {id: $cid})
  RETURN { id: $cid, svgs: COLLECT(DISTINCT(csvg {.*})) } as data
", {cid:c.id}) yield value
RETURN { compartment: apoc.map.mergeList(apoc.coll.flatten(
  apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as data ORDER BY data.compartment.name

UNION

MATCH (:SubsystemState)-[${v}]-(s:Subsystem${m})
CALL apoc.cypher.run("
  MATCH (ss:SubsystemState)-[${v}]-(s:Subsystem {id: $sid})
  RETURN ss { id: $sid, .* } as data
  
  UNION
  
  MATCH (:Subsystem${m} {id: $sid})-[${v}]-(r:Reaction)
  RETURN { id: $sid, reactionCount: COUNT(DISTINCT(r)) } as data

  UNION
  
  MATCH (:Subsystem${m} {id: $sid})-[${v}]-(r:Reaction)
  RETURN { id: $sid, reactionList: COLLECT(DISTINCT(r.id)) } as data
  
  UNION
  
  MATCH (:Subsystem${m} {id: $sid})-[${v}]-(ssvg:SvgMap)
  RETURN { id: $sid, svgs: COLLECT(DISTINCT(ssvg {.*})) } as data
", {sid:s.id}) yield value
RETURN { subsystem: apoc.map.mergeList(apoc.coll.flatten(
  apoc.map.values(apoc.map.groupByMulti(COLLECT(value.data), "id"), [value.data.id])
)) } as data ORDER BY data.subsystem.name
`;

  const customSvgsQuery = `
MATCH (svg:SvgMap${m})
WHERE NOT (svg)--()
RETURN svg { id: svg.id, name: svg.customName, svgs: [svg {.*}]}
`;

  const [componentSvgs, customs] = await Promise.all([
    queryListResult(componentSvgsQuery),
    queryListResult(customSvgsQuery),
  ]);

  const mapListing = {
    compartments: componentSvgs.filter(o => !!o.compartment).reduce((l, o) => [...l, o.compartment] , []),
    subsystems: componentSvgs.filter(o => !!o.subsystem).reduce((l, o) => [...l, o.subsystem] , []),
    customs,
  };

  const compartments = await mapComponents(mapListing.compartments, `${model.slice(0, -3)}-GEM`);
  const subsystems = await mapComponents(mapListing.subsystems, `${model.slice(0, -3)}-GEM`);

  return {...mapListing, compartments, subsystems };
};

const mapSearch = async ({ model, version, searchTerm }) => {
  const [m, v] = parseParams(model, version);

  const statement = `
CALL db.index.fulltext.queryNodes("fulltext", "${searchTerm}~")
YIELD node
OPTIONAL MATCH (node)-[${v}]-(parentNode${m})
WHERE node${m} OR parentNode${m}
RETURN [n in COLLECT(DISTINCT(
	CASE
		WHEN EXISTS(node.id) THEN node.id
		ELSE parentNode.id
	END
))[..100] WHERE n IS NOT NULL]`;

  return querySingleResult(statement);
};
export { getMapsListing, mapSearch };
