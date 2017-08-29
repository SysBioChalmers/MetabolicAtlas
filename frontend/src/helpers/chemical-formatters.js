export function chemicalFormula(value) {
  if (value === null) {
    return '';
  }
  return value.replace(/([0-9])/g, '<sub>$1</sub>');
}

export function chemicalName(value) {
  if (value === null) {
    return '';
  }
  // TODO: Add logic to format formulas
  return value.replace(/([^\s])(\+)([^\s]?)/g, '$1<sup class="top">$2</sup>$3').replace(/H2O/, 'H<sub>2</sub>O');
}

export function chemicalNameExternalLink(value, link) {
  if (value === null) {
    return '';
  }

  if (link === null) {
    return chemicalName(value);
  }

  return `<a
            target='new'
            href='${link}'
          >${chemicalName(value)}</a>`;
}

export function chemicalReaction(value) {
  if (value === null) {
    return '';
  }
  // apply chemical name to all metabolites
  return chemicalName(value).replace(/(=>)/g, '&#8680;');
}
