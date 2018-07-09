// import { default as getLink } from '../helpers/component-link';
import Vue from 'vue';

export default function (c, reactions, relms, rrels, rcomp, rsub) {
  /* eslint-disable no-param-reassign */
  const elms = relms || {};
  const rels = rrels || {};
  let compartmentSet = rcomp;
  if (!compartmentSet) {
    compartmentSet = new Set();
  } else {
    // rcomp is a list
    compartmentSet = new Set(compartmentSet);
  }
  let subsystemSet = rsub;
  if (!subsystemSet) {
    subsystemSet = new Set();
  } else {
    // rsub is a list
    subsystemSet = new Set(subsystemSet);
  }

  let order = 1;
  if (relms || rrels) {
    order = 2;
  }

  for (const r of reactions) {
    const mets = {};
    const reactionComp = new Set();
    subsystemSet.add(...r.subsystem);
    for (const m of [...r.products, ...r.reactants]) {
      const metabolite = {
        id: m.id,
        type: 'metabolite',
        name: m.name,
        formula: m.formula,
        compartment: m.compartment,
        subsystem: new Set(),
        reaction: new Set([r.id]),
      };
      compartmentSet.add(m.compartment);
      reactionComp.add(m.compartment);
      metabolite.subsystem.add(...r.subsystem);
      mets[metabolite.id] = metabolite;
    }

    const mods = {};
    for (const m of r.modifiers) {
      const modifier = {
        id: m.id,
        type: 'enzyme',
        name: m.gene_name || m.id,
        formula: m.formula,
        compartment: {},
        subsystem: new Set(),
        reaction: new Set([r.id]),
      };
      if (reactionComp.size === 1) {
        const compt = reactionComp.values().next().value;
        modifier.compartment[compt] = 1;
      } else {
        // ambigous localization
        reactionComp.forEach((e) => { modifier.compartment[e] = 0; });
      }
      modifier.subsystem.add(...r.subsystem);
      mods[modifier.id] = modifier;
    }

    for (const eid of Object.keys(mods)) {
      const e = mods[eid];
      if (!(eid in elms)) {
        Vue.set(elms, eid, e);
      } else {
        elms[eid].reaction.add(...e.reaction);
        elms[eid].subsystem.add(...e.subsystem);
        for (const cpt of Object.keys(e.compartment)) {
          // new compartment or not ambigous localization for the existing enzyme
          if (!(cpt in elms[eid].compartment) || e.compartment[cpt] === 1) {
            elms[eid].compartment[cpt] = e.compartment[cpt];
          }
        }
      }
    }

    for (const mid of Object.keys(mets)) {
      const m = mets[mid];
      if (!(mid in elms)) {
        Vue.set(elms, mid, m);
      } else {
        elms[mid].reaction.add(...m.reaction);
        elms[mid].subsystem.add(...m.subsystem);
      }
    }

    // add relations between mets-mods components of the current reaction
    for (const eidMo of Object.keys(mods)) {
      for (const eidMe of [...r.reactants]) {
        const relID = `${eidMo}_${eidMe.id}`;
        const relIDinv = `${eidMe.id}_${eidMo}`;
        if (!(relID in rels) && !(relIDinv in rels)) {
          const relation = {
            id: relID,
            source: eidMo,
            target: eidMe.id,
            direction: {},
            order,
          };
          relation.direction[r.id] = r.is_reversible ? 0 : -1;
          relation.reaction = new Set([r.id]);
          rels[relID] = relation;
        } else if (relID in rels) {
          rels[relID].reaction.add(r.id);
          rels[relID].direction[r.id] = r.is_reversible ? 0 : -1;
        } else if (relIDinv in rels) {
          rels[relIDinv].reaction.add(r.id);
          rels[relIDinv].direction[r.id] = r.is_reversible ? 0 : -1;
        }
      }
    }

    // add relations between mets-mods components of the current reaction
    for (const eidMo of Object.keys(mods)) {
      for (const eidMe of [...r.products]) {
        const relID = `${eidMo}_${eidMe.id}`;
        const relIDinv = `${eidMe.id}_${eidMo}`;
        if (!(relID in rels) && !(relIDinv in rels)) {
          const relation = {
            id: relID,
            source: eidMo,
            target: eidMe.id,
            direction: {},
            order,
          };
          relation.direction[r.id] = r.is_reversible ? 0 : 1;
          relation.reaction = new Set([r.id]);
          rels[relID] = relation;
        } else if (relID in rels) {
          rels[relID].reaction.add(r.id);
          rels[relID].direction[r.id] = r.is_reversible ? 0 : 1;
        } else if (relIDinv in rels) {
          rels[relIDinv].reaction.add(r.id);
          rels[relIDinv].direction[r.id] = r.is_reversible ? 0 : 1;
        }
      }
    }

    // add relations between mets components of the current reaction
    // for (const eidReactant of [...r.reactants, ...r.products]) {
    //   for (const eidProduct of [...r.reactants, ...r.products]) {
    //     if (eidReactant.id !== c.id && eidProduct.id !== c.id) {
    //       continue; // eslint-disable-line no-continue
    //     }
    //     const relID = `${eidReactant.id}_${eidProduct.id}`;
    //     const relIDinv = `${eidProduct.id}_${eidReactant.id}`;
    //     if (!(relID in rels) && !(relIDinv in rels)) {
    //       const relation = {
    //         id: relID,
    //         source: eidReactant.id,
    //         target: eidProduct.id,
    //         order,
    //       };
    //       relation.reaction = new Set([r.id]);
    //       rels[relID] = relation;
    //     } else if (relID in rels) {
    //       rels[relID].reaction.add(r.id);
    //     } else if (relIDinv in rels) {
    //       rels[relIDinv].reaction.add(r.id);
    //     }
    //   }
    // }


    // add relations with the main component
    for (const eidMo of Object.keys(mods)) {
      if (eidMo !== c.id) {
        const relID = `${eidMo}_${c.id}`;
        if (!(relID in rels)) {
          const relation = {
            id: `${eidMo}_${c.id}`,
            target: eidMo,
            source: c.id,
            reaction: new Set([r.id]),
            order,
          };
          rels[relID] = relation;
        } else {
          rels[relID].reaction.add(r.id);
        }
      }
    }

    for (const eidMe of Object.keys(mets)) {
      if (eidMe !== c.id) {
        const relID = `${eidMe}_${c.id}`;
        const relIDinv = `${c.id}_${eidMe}`;
        if (relID in rels) {
          rels[relID].reaction.add(r.id);
        } else if (relIDinv in rels) {
          rels[relIDinv].reaction.add(r.id);
        } else {
          const relation = {
            id: `${eidMe}_${c.id}`,
            target: eidMe,
            source: c.id,
            reaction: new Set([r.id]),
            order,
          };
          rels[relID] = relation;
        }
      }
    }
  }
  return [elms, rels, Array.from(compartmentSet), Array.from(subsystemSet)];
}
