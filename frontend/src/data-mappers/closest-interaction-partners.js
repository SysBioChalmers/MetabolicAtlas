import { default as getLink } from '../helpers/component-link';

export default function (c, reactionComponentId, reactions) {
  const elms = {};
  const rels = {};

  const component = {
    id: c.id,
    type: c.component_type,
    short: c.short_name || c.long_name,
    long: c.long_name,
    formula: c.formula,
    compartment: c.compartment,
    link: getLink(c),
    details: c.metabolite || c.enzyme,
  };

  elms[reactionComponentId] = component;

  for (const r of reactions) {
    const mods = {};
    for (const m of r.modifiers) {
      const modifier = {
        id: m.id,
        type: m.component_type,
        short: m.short_name || m.long_name,
        long: m.long_name,
        formula: m.formula,
        compartment: m.compartment,
        reaction: r.id,
        link: getLink(m),
        details: m.metabolite || m.enzyme,
      };

      mods[modifier.id] = modifier;
    }

    const mets = {};
    for (const m of [...r.products, ...r.reactants]) {
      const metabolite = {
        id: m.id,
        type: m.component_type,
        short: m.short_name || m.long_name,
        long: m.long_name,
        formula: m.formula,
        compartment: m.compartment,
        reaction: r.id,
        link: getLink(m),
        details: m.metabolite || m.enzyme,
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
        id: `${eidMo}_${reactionComponentId}`,
        target: eidMo,
        source: reactionComponentId,
        reaction: mods[eidMo].reaction,
      };

      rels[relation.id] = relation;
    }

    for (const eidMe of Object.keys(mets)) {
      const relation = {
        id: `${eidMe}_${reactionComponentId}`,
        target: eidMe,
        source: reactionComponentId,
        reaction: mets[eidMe].reaction,
      };

      rels[relation.id] = relation;
    }
  }

  return [elms, rels];
}
