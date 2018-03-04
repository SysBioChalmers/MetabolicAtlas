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
  return value.replace(/([^\s])(\+)([^\s]?)/g, '$1<sup class="top">+</sup>$3')
  .replace(/H2O/g, 'H<sub>2</sub>O').replace(/(O|H)(2|3)(-?)/g, '$1<sub>$2$3</sub>');
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

export function chemicalReaction(value, r) {
  if (value === null) {
    return '';
  }
  // apply chemical name to all metabolites
  if (r.is_reversible) {
    return chemicalName(value).replace(/(=>)/g, '&#8660;');
  }
  return chemicalName(value).replace(/(=>)/g, '&#8680;');
}
