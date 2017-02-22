export default function (e) {
  const elms = [];
  const rels = [];
  const occ = {};

  const enzyme = {
    id: e.id,
    parentid: 'null',
    type: 'E',
    short: e.short_name,
    long: e.long_name,
    formula: 'formula',
    description: 'description',
    compartment: e.compartment,
  };
  elms.push(enzyme);

  for (const r of e.reactions) {
    const reaction = {
      id: r.reaction_id,
      parentid: 'null',
      type: 'R',
      short: r.reaction_id,
      long: r.reaction_id,
      description: r.reaction_id,
      formula: 'formula',
    };
    elms.push(reaction);

    const relation = {
      id: `${enzyme.id}_${reaction.id}`,
      source: enzyme.id,
      target: reaction.id,
    };
    rels.push(relation);

    for (const p of r.products) {
      const metabolite = {
        id: p.id,
        parentid: p.reaction_id,
        short: p.short_name,
        long: p.long_name,
        description: 'description',
        formula: p.formula,
        compartment: p.compartment,
        type: 'product',
      };
      if (metabolite.id in occ) {
        occ[metabolite.id] += 1;
        metabolite.id = `${metabolite.id}_${occ[metabolite.id]}`;
      } else {
        occ[metabolite.id] = 1;
      }
      elms.push(metabolite);
    }

    for (const re of r.reactants) {
      const metabolite = {
        id: re.id,
        parentid: re.reaction_id,
        short: re.short_name,
        long: re.long_name,
        description: 'description',
        formula: re.formula,
        compartment: re.compartment,
        type: 'reactant',
      };
      if (metabolite.id in occ) {
        occ[metabolite.id] += 1;
        metabolite.id = `${metabolite.id}_${occ[metabolite.id]}`;
      } else {
        occ[metabolite.id] = 1;
      }
      elms.push(metabolite);
    }
  }

  return [elms, rels, occ];
}
