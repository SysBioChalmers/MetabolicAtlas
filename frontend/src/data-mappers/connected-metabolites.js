import { default as getLink } from '../helpers/component-link';

export default function (e) {
  const elms = [];
  const rels = [];
  const occ = {};

  console.log(e);
  const enzyme = {
    id: e.id,
    reactionid: '-',
    parentid: null,
    type: 'enzyme',
    substance_type: 'modifier',
    short: e.short_name || e.long_name,
    long: e.long_name,
    formula: 'formula',
    // description: 'description',
    compartment: e.compartment,
    link: e.uniprot_link || e.ensembl_link,
    details: e.metabolite || e.enzyme,
  };
  elms.push(enzyme);

  for (const r of e.reactions) {
    console.log(r);
    const reaction = {
      id: r.reaction_id,
      reactionid: r.reaction_id,
      parentid: null,
      type: 'reaction',
      short: `${r.reaction_id}\n(${r.subsystem})`,
      long: r.reaction_id,
      // description: r.reaction_id,
      // formula: r.formla,
      subsystem: r.subsystem,
      link: getLink(r),
      // details: r.metabolite || r.enzyme,
    };
    elms.push(reaction);

    const relation = {
      id: `${enzyme.id}_${reaction.id}`,
      source: enzyme.id,
      target: reaction.id,
      type: 'enzyme_reaction',
    };
    rels.push(relation);

    const reactants = {
      id: `${reaction.id}_reactant`,
      parentid: r.reaction_id,
      type: 'reactant_box',
    };
    elms.push(reactants);

    const products = {
      id: `${reaction.id}_product`,
      parentid: r.reaction_id,
      type: 'product_box',
    };
    elms.push(products);

    const relationRp = {
      id: `${r.reaction_id}_rp`,
      source: reactants.id,
      target: products.id,
      type: 'reactants_products',
    };
    rels.push(relationRp);

    for (const p of r.products) {
      const metabolite = {
        id: p.id,
        real_id: p.id, // add because the id is transform below if duplicate => id_2, _3 etc..
        reactionid: r.reaction_id,
        // parentid: r.reaction_id,
        parentid: products.id,
        short: p.short_name || p.long_name,
        long: p.long_name,
        // description: 'description',
        formula: p.formula,
        compartment: p.compartment,
        substance_type: 'product',
        type: 'metabolite',
        link: getLink(p),
        details: p.metabolite || p.enzyme,
        isCurrencyMetabolite: p.currency_metabolites.length > 0,
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
        real_id: re.id,
        reactionid: r.reaction_id,
        // parentid: r.reaction_id,
        parentid: reactants.id,
        short: re.short_name || re.long_name,
        long: re.long_name,
        // description: 'description',
        formula: re.formula,
        compartment: re.compartment,
        substance_type: 'reactant',
        type: 'metabolite',
        link: getLink(re),
        details: re.metabolite || re.enzyme,
        isCurrencyMetabolite: re.currency_metabolites.length > 0,
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
