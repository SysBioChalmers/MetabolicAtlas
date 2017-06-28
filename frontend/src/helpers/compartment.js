
const compartmentData = {
  extracellular: { letter: 's', color: '' },
  peroxisome: { letter: 'p', color: '' },
  mitochondria: { letter: 'm', color: '' },
  cytosol: { letter: 'c', color: '' },
  lysosome: { letter: 'l', color: '' },
  'endoplasmic reticulum': { letter: 'r', color: '' },
  'golgi apparatus': { letter: 'g', color: '' },
  nucleus: { letter: 'n', color: '' },
  boundary: { letter: 'x', color: '' },
  s: { name: 'Extracellular', color: '' },
  p: { name: 'Peroxisome', color: '' },
  m: { name: 'Mitochondria', color: '' },
  c: { name: 'Cytosol', color: '' },
  l: { name: 'Lysosome', color: '' },
  r: { name: 'Endoplasmic reticulum', color: '' },
  g: { name: 'Golgi apparatus', color: '' },
  n: { name: 'Nucleus', color: '' },
  x: { name: 'Boundary', color: '' },
};

export function getCompartmentInfoFromID(id) {
  if (compartmentData(id[0])) {
    return compartmentData(id[0]);
  }
  return null;
}

export function getCompartmentInfoFromName(name) {
  if (compartmentData(name)) {
    return compartmentData(name);
  }
  return null;
}

function formatSpan(x) {
  const regex = /(.+)\[(.)\]/g;
  const match = regex.exec(x);
  return `${match[1]}<span class="sc" title="${compartmentData[match[2]].name}">${match[2]}</span>`;
}

export function reformatChemicalReaction(value) {
  if (value === null) {
    return '';
  }
  const arr = value.split(' &#8680; ');

  let reactants = arr[0].split(' + ');
  reactants = reactants.map(formatSpan).join(' + ');

  let products = arr[1].split(' + ');
  products = products.map(formatSpan).join(' + ');

  return `${reactants} &#8680; ${products}`;
}
