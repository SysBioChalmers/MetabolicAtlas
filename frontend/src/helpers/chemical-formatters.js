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
  return value.replace(/(\+)/g, '<sup>$1</sup>');
}

export function chemicalNameLink(value) {
  if (value === null) {
    return '';
  }

  return `<a
            target='new'
            href='https://pubchem.ncbi.nlm.nih.gov/compound/${value}'
          >${chemicalName(value)}</a>`;
}
