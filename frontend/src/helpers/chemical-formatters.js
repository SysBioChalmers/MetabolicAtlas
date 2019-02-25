export function chemicalFormula(value) {
  if (value === null || value === undefined) {
    return '';
  }
  return value.replace(/([0-9])/g, '<sub>$1</sub>');
}

export function chemicalName(value) {
  if (value === null || value === undefined) {
    return '';
  }
  // TODO: Add logic to format formulas
  return value.replace(/([^\s])(\+)([^\s]?)/g, '$1<sup class="top">+</sup>$3')
  .replace(/H2O/g, 'H<sub>2</sub>O').replace(/(O|H)(2|3)(-?)/g, '$1<sub>$2$3</sub>');
}


// TODO look about rel=noopener
export function chemicalNameExternalLink(value, link) {
  if (value === null || value === undefined) {
    return '';
  }

  if (link === null) {
    return chemicalName(value);
  }

  return `<a
            target='_blank'
            href='${link}'
          >${chemicalName(value)}</a>`;
}

function chemicalReactionSign(value, reversible) {
  if (value === null) {
    return '';
  }
  // apply chemical name to all metabolites
  if (reversible) {
    return chemicalName(value).replace(/(=>)/g, '&#8660;');
  }
  return chemicalName(value).replace(/(=>)/g, '&#8680;');
}

export function chemicalReaction(value, r) {
  if (typeof r !== 'boolean' && 'is_reversible' in r) {
    return chemicalReactionSign(value, r.is_reversible);
  }
  return chemicalReactionSign(value, r);
}

function formatSpan(currentVal, index, array, elements, addComp) {
  const regex = /([0-9]+ )?(.+)\[([a-z]{1,3})\]/g;
  const match = regex.exec(currentVal);
  if (!addComp) {
    return `${match[1] ? match[1] : ''}<m class="${elements[index]}">${match[2]}</m>`;
  }
  return `${match[1] ? match[1] : ''}<m class="${elements[index]}">${match[2]}</m>
    <span class="sc" title="${this.compartmentLetters[match[3]]}">${match[3]}</span>`;
}


export function reformatChemicalReactionLink(reaction) {
  if (reaction === null) {
    return '';
  }
  const addComp = reaction.compartment.includes('=>');
  let eqArr = null;
  if (reaction.is_reversible) {
    eqArr = reaction.equation.split(' &#8660; ');
  } else {
    eqArr = reaction.equation.split(' &#8658; ');
  }
  if (eqArr.length === 1) {
    eqArr = reaction.equation.split(' => ');
  }
  const idEqArr = reaction.id_equation.split(' => ');
  let reactants = '';
  let products = '';
  if (idEqArr[0]) {
    const idReactants = idEqArr[0].split(' + ');
    reactants = eqArr[0].split(' + ').map(
      (x, i, a) => formatSpan(x, i, a, idReactants, addComp)
    ).join(' + ');
  }
  if (idEqArr[1]) {
    const idProducts = idEqArr[1].split(' + ');
    products = eqArr[1].split(' + ').map(
      (x, i, a) => formatSpan(x, i, a, idProducts, addComp)
    ).join(' + ');
  }

  if (reaction.is_reversible) {
    return `${reactants} &#8660; ${products}`;
  }
  return `${reactants} &#8658; ${products}`;
}
