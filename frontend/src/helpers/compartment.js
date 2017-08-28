
const data = {
  extracellular: {
    name: 'Extracellular',
    letter: 's',
    color: '',
    svgName: 'fakesvg',
    compartmentID: 1,
  },
  peroxisome: {
    name: 'Peroxisome',
    letter: 'p',
    color: '',
    svgName: '',
    compartmentID: 2,
  },
  mitochondria: {
    name: 'Mitochondria',
    letter: 'm',
    color: '',
    svgName: '',
    compartmentID: 3,
  },
  cytosol: {
    name: 'Cytosol',
    letter: 'c',
    color: '',
    svgName: '',
    compartmentID: 4,
  },
  lysosome: {
    name: 'Lysosome',
    letter: 'l',
    color: '',
    svgName: '',
    compartmentID: 5,
  },
  'endoplasmic reticulum': {
    name: 'Endoplasmic reticulum',
    letter: 'r',
    color: '',
    svgName: 'ERtestwithid',
    compartmentID: 6,
  },
  'golgi apparatus': {
    name: 'Golgi apparatus',
    letter: 'g',
    color: '',
    svgName: '',
    compartmentID: 7,
  },
  nucleus: {
    name: 'Nucleus',
    letter: 'n',
    color: '',
    svgName: 'nucleus_no_min',
    compartmentID: 8,
  },
  boundary: {
    name: 'Boundary',
    letter: 'x',
    color: '',
    svgName: '',
    compartmentID: 9,
  },
};

const l = {
  s: data.extracellular,
  p: data.peroxisome,
  m: data.mitochondria,
  c: data.cytosol,
  l: data.lysosome,
  r: data['endoplasmic reticulum'],
  g: data['golgi apparatus'],
  n: data.nucleus,
  x: data.boundary,
};

const d = {
  1: data.extracellular,
  2: data.peroxisome,
  3: data.mitochondria,
  4: data.cytosol,
  5: data.lysosome,
  6: data['endoplasmic reticulum'],
  7: data['golgi apparatus'],
  8: data.nucleus,
  9: data.boundary,
};

export function getCompartmentFromLetter(letter) {
  if (l[letter]) {
    return l[letter];
  }
  return null;
}

export function getCompartmentFromID(id) {
  const lastChar = id[id.length - 1];
  return getCompartmentFromLetter(lastChar);
}

export function getCompartmentFromName(name) {
  if (data[name]) {
    return data[name];
  }
  return null;
}

export function getCompartmentFromCID(compartmentID) {
  if (d[compartmentID]) {
    return d[compartmentID];
  }
  return null;
}

function formatSpan(currentVal, index, array, elements) {
  const regex = /(.+)\[(.)\]/g;
  const match = regex.exec(currentVal);
  return `<rc id="${elements[index].id}">${match[1]}</rc><span class="sc" title="${l[match[2]].name}">${match[2]}</span>`;
}

export function reformatChemicalReaction(equation, reaction) {
  console.log(reaction);
  if (reaction === null || equation === null) {
    return '';
  }
  const arr = equation.split(' &#8680; ');

  // assumes the order in reaction.reactants (reps. reaction.products)
  // are identique to the order or the reactants (resp. products) of the equation

  let reactants = arr[0].split(' + ');
  reactants = reactants.map(
    (x, i, a) => formatSpan(x, i, a, reaction.reactants)).join(' + ');

  let products = arr[1].split(' + ');
  products = products.map(
    (x, i, a) => formatSpan(x, i, a, reaction.products)).join(' + ');

  return `${reactants} &#8680; ${products}`;
}

export function getCompartmentCount() {
  return Object.keys(d).length;
}

export function getCompartments() {
  return data;
}
