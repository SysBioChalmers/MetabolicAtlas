// import { default as getLink } from '../helpers/component-link';

export default function (c, reactions) {
  const elms = {};
  const rels = {};

  const component = {
    id: c.id,
    type: c.type,
    name: c.gene_name || c.name || c.id,
    formula: c.formula,
    compartment: c.compartment,
    // link: getLink(c),
    // details: c.metabolite || c.enzyme,
  };

  elms[component.id] = component;

  for (const r of reactions) {
    const mods = {};
    for (const m of r.modifiers) {
      const modifier = {
        id: m.id,
        type: 'enzyme',
        name: m.gene_name || m.id,
        formula: m.formula,
        compartment: m.compartment,
        reaction: r.id,
        // link: getLink(m),
        // details: m.metabolite || m.enzyme,
      };

      mods[modifier.id] = modifier;
    }

    const mets = {};
    for (const m of [...r.products, ...r.reactants]) {
      const metabolite = {
        id: m.id,
        type: 'metabolite',
        name: m.name,
        formula: m.formula,
        compartment: m.compartment,
        reaction: r.id,
        // link: getLink(m),
        // details: m.metabolite || m.enzyme,
      };

      mets[metabolite.id] = metabolite;
    }

    for (const eid of Object.keys(mods)) {
      if (!(eid in Object.keys(elms))) {
        elms[eid] = mods[eid];
      }
    }

    for (const eid of Object.keys(mets)) {
      if (!(eid in Object.keys(elms))) {
        elms[eid] = mets[eid];
      }
    }

    for (const eidMo of Object.keys(mods)) {
      for (const eidMe of Object.keys(mets)) {
        const relation = {
          id: `${eidMo}_${eidMe}`,
          source: eidMo,
          target: eidMe,
        };

        if (!(relation.id in Object.keys(rels))) {
          const mod = mods[eidMo];
          const met = mets[eidMe];

          if (mod.reaction && mod.reaction === met.reaction) {
            relation.reaction = mod.reaction;
            rels[relation.id] = relation;
          }
        }
      }
    }

    for (const eidMo of Object.keys(mods)) {
      const relation = {
        id: `${eidMo}_${component.id}`,
        target: eidMo,
        source: component.id,
        reaction: mods[eidMo].reaction,
      };

      rels[relation.id] = relation;
    }

    for (const eidMe of Object.keys(mets)) {
      const relation = {
        id: `${eidMe}_${component.id}`,
        target: eidMe,
        source: component.id,
        reaction: mets[eidMe].reaction,
      };

      rels[relation.id] = relation;
    }
  }

  return [elms, rels];
}
