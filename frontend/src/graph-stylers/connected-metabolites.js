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
          reactionid: elm.reactionid,
          name: elm.short,
          hpaLink: `http://www.proteinatlas.org/${elm.long}/tissue#top`, // TODO: move into config
          link: elm.link,
          type: elm.type,
          details: elm.details,
        },
      });
    } else {
      elmsjson.push({
        group: 'nodes',
        data: {
          id: elm.id,
          reactionid: elm.reactionid,
          name: elm.short,
          hpaLink: `http://www.proteinatlas.org/${elm.long}/tissue#top`, // TODO: move into config
          link: elm.link,
          details: elm.details,
        },
      });
    }
  }

  for (const rel of rels) {
    elmsjson.push({
      group: 'edges',
      data: {
        id: rel.id,
        type: rel.type,
        source: rel.source,
        target: rel.target,
      },
    });
  }

  const reactionColor = '#C5F4DD';
  const metaboliteColor = '#259F64';
  const textColor = '#363636';
  const lineColor = '#CBDBDB';

  const stylesheet = cytoscape.stylesheet()
    .selector('node')
    .css({
      content: 'data(name)',
      'font-size': '20px',
      'text-valign': 'bottom',
      'text-wrap': 'wrap',
      shape: 'circle',
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
      'background-color': reactionColor,
      'background-opacity': 0.3,
    })
    .selector('node > node') // parent node selector, eg the metabolites inside the reactions
    .css({
      'font-size': '9px',
      'padding-top': '1px',
      'padding-left': '1px',
      'padding-bottom': '1px',
      'padding-right': '1px',
      'text-valign': 'top',
      'text-halign': 'center',
      'background-color': metaboliteColor,
      shape: 'heptagon',
      width: 20,
      height: 20,
    })
    .selector('node[type="reactant_box"]')
    .css({
      'background-color': 'blue',
    })
    .selector('node[type="product_box"]')
    .css({
      'background-color': 'red',
    })
    .selector('node[type="enzyme"]')
    .css({
      'font-size': '15px',
    })
    .selector('node[type="product"]') // select the products and make them rectangular instead
    .css({ shape: 'triangle' })
    .selector('edge') // please note that right now the only edge is from main enzyme to the reactions!
    .css({
      width: 4,
      'line-color': lineColor,
      'target-arrow-color': lineColor,
      'target-arrow-shape': 'triangle',
    })
    .selector('edge[type="reactants_products"]')
    .css({
      width: 3,
      'line-color': 'black',
      'target-arrow-color': 'black',
      'target-arrow-shape': 'triangle',
    })
    .selector(':selected')
    .css({
      'background-color': textColor,
      'line-color': textColor,
      'target-arrow-color': textColor,
      'source-arrow-color': textColor,
      'text-outline-color': textColor,
    })
    .selector('core')
    .css({
      // the circle visible when clicking on the graph
      'active-bg-color': '#64CC9A',
      'active-bg-opacity': 0.25,
      'active-bg-size': 10,
    });

  console.log(elmsjson);
  return [elmsjson, stylesheet];
}
