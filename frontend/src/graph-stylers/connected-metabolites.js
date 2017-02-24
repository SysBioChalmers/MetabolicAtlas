import cytoscape from 'cytoscape';

export default function (elms, rels) {
  const elmsjson = [];

  for (const elm of elms) {
    if (elm.parentid !== 'null') {
      elmsjson.push({
        group: 'nodes',
        data: {
          id: elm.id,
          parent: elm.parentid,
          name: elm.short || elm.long,
          type: elm.type,
        },
      });
    } else {
      elmsjson.push({
        group: 'nodes',
        data: {
          id: elm.id,
          name: elm.short || elm.long,
        },
      });
    }
  }

  for (const rel of rels) {
    elmsjson.push({
      group: 'edges',
      data: {
        id: rel.id,
        source: rel.source,
        target: rel.target,
      },
    });
  }

  const stylesheet = cytoscape.stylesheet()
    .selector('node')
    .css({
      content: 'data(name)',
      'font-size': '30px',
    })
    .selector('$node > node')
    .css({
      'font-size': '10px',
      'padding-top': '20px', // not super useful as it only affects node to parent node distance
      'padding-left': '20px',
      'padding-bottom': '20px',
      'padding-right': '20px',
      'text-valign': 'top',
      'text-halign': 'center',
      'background-color': '#000055',
      'background-opacity': 0.3,
    })
    .selector('node > node') // parent node selector, eg the metabolites inside the reactions
    .css({
      'font-size': '8px',
      'padding-top': '1px',
      'padding-left': '1px',
      'padding-bottom': '1px',
      'padding-right': '1px',
      'text-valign': 'top',
      'text-halign': 'center',
      'background-color': '#0c650c',
      shape: 'heptagon',
      width: 20,
      height: 20,
    })
    .selector('node[type="product"]') // select the products and make them rectangular instead
    .css({ shape: 'octagon' })
    .selector('edge') // please note that right now the only edge is from main enzyme to the reactions!
    .css({
      width: 3,
      'line-color': '#ccc',
      'target-arrow-color': '#ccc',
      'target-arrow-shape': 'triangle',
    })
    .selector(':selected')
    .css({
      'background-color': 'black',
      'line-color': 'black',
      'target-arrow-color': 'black',
      'source-arrow-color': 'black',
      'text-outline-color': 'black',
    });

  return [elmsjson, stylesheet];
}
