export const buildCustomLink = ({ model, type, id, title, cssClass }) => `<a href="/explore/${model}/gem-browser/${type}/${id}" class="custom-router-link ${cssClass || ''}">${title}</a>`;

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

export function equationSign(isReversible) {
  return isReversible ? '⇔' : '⇒';
}

export function addMassUnit(value) {
  return `${value} g/mol`;
}

export function getSimpleEquation(reaction) {
  if (reaction === null) {
    return '';
  }
  const reactants = reaction.reactants.join(' + ');
  const products = reaction.products.join(' + ');
  return `${reactants} ${equationSign(reaction.reversible)} ${products}`;
}

export function getChemicalReaction(reaction) {
  if (reaction === null) {
    return '';
  }
  const reactants = reaction.reactants.map(
    x => `${x.stoichiometry !== 1 ? `${x.stoichiometry} ` : ''}${x.fullName}`
  ).join(' + ');
  const products = reaction.products.map(
    x => `${x.stoichiometry !== 1 ? `${x.stoichiometry} ` : ''}${x.fullName}`
  ).join(' + ');
  return `${reactants} ${equationSign(reaction.reversible)} ${products}`;
}

const sortByName = metabolites => [...metabolites].sort((a, b) => ((a.name > b.name) ? 1 : -1));

// TODO: consider using an object as param
export function reformatChemicalReactionHTML(reaction, noLink = false, model = 'human-gem', sourceMet = '') {
  if (reaction === null) {
    return '';
  }
  const addComp = reaction.compartment_str.includes('=>');
  const type = 'metabolite';
  function formatReactionElement(x) {
    if (!addComp) {
      return `${Math.abs(x.stoichiometry) !== 1 ? x.stoichiometry : ''} ${noLink ? x.name : buildCustomLink({ model, type, id: x.id, cssClass: x.id === sourceMet ? 'cms' : undefined, title: x.name })}`;
    }
    const regex = /.+\[([a-z]{1,3})\]$/;
    const match = regex.exec(x.fullName);
    return `${Math.abs(x.stoichiometry !== 1) ? x.stoichiometry : ''} ${noLink ? x.name : buildCustomLink({ model, type, id: x.id, cssClass: x.id === sourceMet ? 'cms' : undefined, title: x.name })}<span class="sc" title="${x.compartment}">${match[1]}</span>`;
  }

  const reactants = sortByName(reaction.reactants).map(formatReactionElement).join(' + ');
  const products = sortByName(reaction.products).map(formatReactionElement).join(' + ');

  return `${reactants} ${equationSign(reaction.reversible)} ${products}`;
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
  return `${reactantsCompartmentsStr} ${equationSign(reaction.reversible)} ${productsCompartmentsStr}`;
};

export const generateSocialMetaTags = ({ title, description }) => [
  { name: 'description', vmid: 'description', content: description },
  { property: 'og:title', vmid: 'og:title', content: title },
  { property: 'og:description', vmid: 'og:description', content: description },
  { property: 'twitter:title', vmid: 'twitter:title', content: title },
  { property: 'twitter:description', vmid: 'twitter:description', content: description },
];
