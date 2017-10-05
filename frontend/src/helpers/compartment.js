
const data = {
  wholemap: {
    name: 'Whole map',
    letter: '',
    svgName: 'whole_metabolic_network_without_details',
    compartmentID: 0,
    maxZoomLvl: 10,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  extracellular: {
    name: 'Extracellular',
    letter: 's',
    color: '',
    svgName: 'fakesvg',
    compartmentID: 13,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  cytosol: {
    name: 'Cytosol',
    letter: 'c',
    color: '',
    svgName: '',
    compartmentID: 15,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  peroxisome: {
    name: 'Peroxisome',
    letter: 'p',
    color: '',
    svgName: 'peroxisome',
    compartmentID: 1,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  mitochondria: {
    name: 'Mitochondria',
    letter: 'm',
    color: '',
    svgName: 'mitochondrion',
    // svgName: 'fakesvg',
    compartmentID: 2,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  lysosome: {
    name: 'Lysosome',
    letter: 'l',
    color: '',
    svgName: 'lysosome',
    compartmentID: 3,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  'endoplasmic reticulum': {
    name: 'ER',
    letter: 'r',
    color: '',
    svgName: 'ER',
    compartmentID: 4,
    maxZoomLvl: 30,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 5,
      metaboliteLabel: 10,
      reaction: 5,
      reactionLabel: 10,
      'flux-edge': 8,
      'effector-edge': 8,
    },
  },
  'golgi apparatus': {
    name: 'Golgi apparatus',
    letter: 'g',
    color: '',
    svgName: 'golgi',
    compartmentID: 5,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  nucleus: {
    name: 'Nucleus',
    letter: 'n',
    color: '',
    svgName: 'nucleus',
    compartmentID: 6,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  boundary: {
    name: 'Boundary',
    letter: 'x',
    color: '',
    svgName: '',
    compartmentID: 14,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  cytosol1: {
    name: 'Cytosol_1',
    letter: 'c1',
    color: '',
    svgName: 'cytosol_1',
    compartmentID: 7,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  cytosol2: {
    name: 'Cytosol_2',
    letter: 'c2',
    color: '',
    svgName: 'cytosol_2',
    compartmentID: 8,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  cytosol3: {
    name: 'Cytosol_3',
    letter: 'c3',
    color: '',
    svgName: 'cytosol_3',
    compartmentID: 9,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  cytosol4: {
    name: 'Cytosol_4',
    letter: 'c4',
    color: '',
    svgName: 'cytosol_4',
    compartmentID: 10,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  cytosol5: {
    name: 'Cytosol_5',
    letter: 'c5',
    color: '',
    svgName: 'cytosol_5',
    compartmentID: 11,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
  },
  cytosol6: {
    name: 'Cytosol_6',
    letter: 'c6',
    color: '',
    svgName: 'cytosol_6',
    compartmentID: 12,
    maxZoomLvl: 10,
    minZoomLvl: 1,
    RenderZoomLvl: {
      metabolite: 2,
      metaboliteLabel: 5,
      reaction: 2,
      reactionLabel: 5,
      'flux-edge': 3,
      'effector-edge': 3,
    },
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
  c1: data.cytosol1,
  c2: data.cytosol2,
  c3: data.cytosol3,
  c4: data.cytosol4,
  c5: data.cytosol5,
  c6: data.cytosol6,
};

const d = {
  0: data.wholemap,
  13: data.extracellular,
  1: data.peroxisome,
  2: data.mitochondria,
  3: data.lysosome,
  4: data['endoplasmic reticulum'],
  5: data['golgi apparatus'],
  6: data.nucleus,
  14: data.boundary,
  7: data.cytosol1,
  8: data.cytosol2,
  9: data.cytosol3,
  10: data.cytosol4,
  11: data.cytosol5,
  12: data.cytosol6,
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
  if (data[name.toLowerCase()]) {
    return data[name.toLowerCase()];
  }
  return null;
}

export function getCompartmentFromCID(compartmentID) {
  if (d[compartmentID]) {
    return d[compartmentID];
  }
  return null;
}


function formatSpan(currentVal, index, array, elements, addComp) {
  const regex = /(.+)\[(.)\]/g;
  const match = regex.exec(currentVal);
  if (!addComp) {
    return `<rc id="${elements[index].id}">${match[1]}</rc>`;
  }
  return `<rc id="${elements[index].id}">${match[1]}</rc><span class="sc" title="${l[match[2]].name}">${match[2]}</span>`;
}

export function reformatChemicalReaction(equation, reaction) {
  if (reaction === null || equation === null) {
    return '';
  }
  const addComp = reaction.compartment.includes('=>');
  let arr = equation.split(' &#8680; ');
  if (arr.length === 1) {
    arr = equation.split(' => ');
  }

  // assumes the order in reaction.reactants (reps. reaction.products)
  // are identique to the order or the reactants (resp. products) of the equation

  let reactants = arr[0].split(' + ');
  reactants = reactants.map(
    (x, i, a) => formatSpan(x, i, a, reaction.reactants, addComp)).join(' + ');

  let products = arr[1].split(' + ');
  products = products.map(
    (x, i, a) => formatSpan(x, i, a, reaction.products, addComp)).join(' + ');

  return `${reactants} &#8680; ${products}`;
}

export function getCompartmentCount() {
  return Object.keys(d).length;
}

export function getCompartments() {
  return data;
}
