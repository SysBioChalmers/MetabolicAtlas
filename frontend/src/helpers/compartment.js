
const data = {
  wholemap: {
    name: 'Whole map',
    letter: '',
    svgName: 'whole_metabolic_network_without_details',
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
    maxZoomLvl: 15,
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
  lysosome: {
    name: 'Lysosome',
    letter: 'l',
    color: '',
    svgName: 'lysosome',
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
    name: 'Endoplasmic reticulum',
    letter: 'r',
    color: '',
    svgName: 'ER',
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
  cytosol_1: {
    name: 'Cytosol_1',
    letter: 'c1',
    color: '',
    svgName: 'cytosol_1',
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
  cytosol_2: {
    name: 'Cytosol_2',
    letter: 'c2',
    color: '',
    svgName: 'cytosol_2',
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
  cytosol_3: {
    name: 'Cytosol_3',
    letter: 'c3',
    color: '',
    svgName: 'cytosol_3',
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
  cytosol_4: {
    name: 'Cytosol_4',
    letter: 'c4',
    color: '',
    svgName: 'cytosol_4',
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
  cytosol_5: {
    name: 'Cytosol_5',
    letter: 'c5',
    color: '',
    svgName: 'cytosol_5',
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
  cytosol_6: {
    name: 'Cytosol_6',
    letter: 'c6',
    color: '',
    svgName: 'cytosol_6',
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
  if (name && data[name.toLowerCase()]) {
    return data[name.toLowerCase()];
  }
  return null;
}

/*
function formatSpan(currentVal, index, array, elements, addComp) {
  const regex = /(.+)\[(.)\]/g;
  const match = regex.exec(currentVal);
  if (!addComp) {
    return `<m class="${elements[index].id}">${match[1]}</m>`;
  }
  return `<m class="${elements[index].id}">${match[1]}
  </m><span class="sc" title="${l[match[2]].name}">${match[2]}</span>`;
}*/

function formatSpan(currentVal, index, array, elements, addComp) {
  const regex = /([0-9]+ )?(.+)\[([a-z]{1,3})\]/g;
  const match = regex.exec(currentVal);
  if (!addComp) {
    return `${match[1] ? match[1] : ''}<m class="${elements[index]}">${match[2]}</m>`;
  }
  return `${match[1] ? match[1] : ''}<m class="${elements[index]}">${match[2]}</m>
    <span class="sc" title="${l[match[3]].name}">${match[3]}</span>`;
}

/*
export function reformatChemicalReaction(equation, reaction) {
  if (reaction === null || equation === null) {
    return '';
  }
  const addComp = reaction.compartment.includes('=>');
  let arr = null;
  if (reaction.is_reversible) {
    arr = equation.split(' &#8660; ');
  } else {
    arr = equation.split(' &#8680; ');
  }
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

  if (reaction.is_reversible) {
    return `${reactants} &#8660; ${products}`;
  }
  return `${reactants} &#8680; ${products}`;
}
*/

export function reformatChemicalReaction(reaction) {
  if (reaction === null) {
    return '';
  }
  const addComp = reaction.compartment.includes('=>');
  let eqArr = null;
  if (reaction.is_reversible) {
    eqArr = reaction.equation.split(' &#8660; ');
  } else {
    eqArr = reaction.equation.split(' &#8680; ');
  }
  if (eqArr.length === 1) {
    eqArr = reaction.equation.split(' => ');
  }
  const idEqArr = reaction.id_equation.split(' => ');
  const idReactants = idEqArr[0].split(' + ');
  const idProducts = idEqArr[1].split(' + ');
  const reactants = eqArr[0].split(' + ').map(
      (x, i, a) => formatSpan(x, i, a, idReactants, addComp)
    ).join(' + ');
  const products = eqArr[1].split(' + ').map(
      (x, i, a) => formatSpan(x, i, a, idProducts, addComp)
    ).join(' + ');

  if (reaction.is_reversible) {
    return `${reactants} &#8660; ${products}`;
  }
  return `${reactants} &#8680; ${products}`;
}

export function getCompartmentCount() {
  return Object.keys(l).length;
}

export function getCompartments() {
  return data;
}
