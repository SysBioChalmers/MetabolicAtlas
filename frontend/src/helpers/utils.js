export const buildCustomLink = ({ model, type, id, title, cssClass }) => `<a href="/explore/gem-browser/${model}/${type}/${id}" class="custom-router-link ${cssClass || ''}">${title}</a>`;

export function capitalize(value) {
  return `${value[0].toUpperCase()}${value.slice(1)}`;
}

export function idfy(value) {
  if (!value) {
    return '';
  }
  let s = value.toLowerCase().replace(/[^0-9a-z_]/g, '_');
  s = s.replace(/_{2,}/g, '_');
  return s.replace(/^_|_$/, '');
}

export function replaceUnderscores(value) {
  return `${value.replace('_', ' ')}`;
}

export const convertCamelCase = str => str.replace(/([a-z\xE0-\xFF])([A-Z\xC0\xDF])/g, '$1 $2').toLowerCase();

export function reformatTableKey(value) {
  return replaceUnderscores(capitalize(value));
}

export function reformatStringToLink(value, link) {
  if (link) {
    return `<a href="${link}" target="_blank">${value}</a>`;
  }
  return `<a href="${value}" target="_blank">${value}</a>`;
}

export function reformatEqSign(equation, reversible) {
  if (reversible) {
    return equation.replace(' => ', ' &#8660; ');
  }
  return equation.replace(' => ', ' &#8658; ');
}

export function addMassUnit(value) {
  return `${value} g/mol`;
}

export function joinListElements(list) {
  let output = '';
  if (list.length) {
    output = list.join('; ');
  }
  return output;
}

export function replaceEmpty(value) {
  if (!value || value === null) {
    return '-';
  }
  return value;
}

export function reformatSBOLink(sboID, link) {
  if (link) {
    return reformatStringToLink(sboID, link);
  }
  return `<a href="http://www.ebi.ac.uk/sbo/main/${sboID}" target="_blank">${sboID}</a>`;
}

export function getChemicalReaction(reaction) {
  if (reaction === null) {
    return '';
  }
  const reactants = reaction.reactionreactant_set.map(
    x => `${x.stoichiometry !== 1 ? `${x.stoichiometry} ` : ''}${x.fullName}`
  ).join(' + ');
  const products = reaction.reactionproduct_set.map(
    x => `${x.stoichiometry !== 1 ? `${x.stoichiometry} ` : ''}${x.fullName}`
  ).join(' + ');

  if (reaction.reversible) {
    return `${reactants} <=> ${products}`;
  }
  return `${reactants} => ${products}`;
}

const sortByName = metabolites => [...metabolites].sort((a, b) => ((a.name > b.name) ? 1 : -1));

// TODO: consider using an object as param
export function reformatChemicalReactionHTML(reaction, noLink = false, model = 'human-gem', sourceMet = '') {
  if (reaction === null) {
    return '';
  }
  const addComp = reaction.is_transport || reaction.compartment_str.includes('=>');
  const type = 'metabolite';
  function formatReactionElement(x) {
    if (!addComp) {
      return `${Math.abs(x.stoichiometry) !== 1 ? x.stoichiometry : ''} ${noLink ? x.name : buildCustomLink({ model, type, id: x.id, cssClass: x.id === sourceMet ? 'cms' : undefined, title: x.name })}`;
    }
    const regex = /.+\[([a-z]{1,3})\]$/;
    const match = regex.exec(x.fullName);
    return `${Math.abs(x.stoichiometry !== 1) ? x.stoichiometry : ''} ${noLink ? x.name : buildCustomLink({ model, type, id: x.id, cssClass: x.id === sourceMet ? 'cms' : undefined, title: x.name })}<span class="sc" title="${x.compartment}">${match[1]}</span>`;
  }

  const reactants = sortByName(reaction.reactionreactant_set).map(formatReactionElement).join(' + ');
  const products = sortByName(reaction.reactionproduct_set).map(formatReactionElement).join(' + ');

  if (reaction.reversible) {
    return `${reactants} &#8660; ${products}`;
  }
  return `${reactants} &#8658; ${products}`;
}

export function sortResults(a, b, searchTermString) {
  let matchSizeDiffA = 100;
  let matchedStringA = '';
  Object.values(a).forEach((v) => {
    if (v && (typeof v === 'string' || v instanceof String)
      && v.toLowerCase().includes(searchTermString.toLowerCase())) {
      const diff = v.length - searchTermString.length;
      if (diff < matchSizeDiffA) {
        matchSizeDiffA = diff;
        matchedStringA = v;
      }
    }
  });

  let matchSizeDiffB = 100;
  let matchedStringB = '';

  Object.values(b).forEach((v) => {
    if (v && (typeof v === 'string' || v instanceof String)
      && v.toLowerCase().includes(searchTermString.toLowerCase())) {
      const diff = v.length - searchTermString.length;
      if (diff < matchSizeDiffB) {
        matchSizeDiffB = diff;
        matchedStringB = v;
      }
    }
  });
  if (matchSizeDiffA === matchSizeDiffB) {
    return matchedStringA.localeCompare(matchedStringB);
  }
  return matchSizeDiffA < matchSizeDiffB ? -1 : 1;
}

export const constructCompartmentStr = (reaction) => {
  const compartments = reaction.compartments.reduce((obj, { id, ...cs }) => ({
    ...obj,
    [id]: cs,
  }), {});

  const reactants = reaction.metabolites.filter(m => m.outgoing);
  const products = reaction.metabolites.filter(m => !m.outgoing);
  const reactantsCompartments = new Set(
    reactants.map(r => compartments[r.compartmentId].name).sort()
  );
  const productsCompartments = new Set(
    products.map(r => compartments[r.compartmentId].name).sort()
  );

  const reactantsCompartmentsStr = Array.from(reactantsCompartments).join(' + ');
  if (JSON.stringify([...reactantsCompartments])
    === JSON.stringify([...productsCompartments])) {
    return reactantsCompartmentsStr;
  }

  const productsCompartmentsStr = Array.from(productsCompartments).join(' + ');
  return `${reactantsCompartmentsStr} => ${productsCompartmentsStr}`;
};
