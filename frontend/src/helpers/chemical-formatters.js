export function chemicalFormula(value) {
  if (value === null) {
    return '';
  }
  return value.replace(/([0-9])/g, '<sup>$1</sup>');
}

export function chemicalName(value) {
  if (value === null) {
    return '';
  }
  // TODO: Add logic to format formulas
  return value.replace(/(\+)/g, '<sup class="top">$1</sup>');
}

export function chemicalNameLink(value, link) {
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
