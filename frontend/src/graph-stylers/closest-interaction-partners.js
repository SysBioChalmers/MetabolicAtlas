import cytoscape from 'cytoscape';

export default function (elms, rels) {
  const elmsjson = [];

  for (const id of Object.keys(elms)) {
    const elm = elms[id];

    elmsjson.push({
      group: 'nodes',
      data: {
        id: elm.id,
        name: elm.short,
        hpaLink: `http://www.proteinatlas.org/${elm.long}/tissue#top`, // TODO: movie into config
        type: elm.type,
        details: elm.details,
      },
    });
  }

  for (const id of Object.keys(rels)) {
    const rel = rels[id];

    elmsjson.push({
      group: 'edges',
      data: {
        id: rel.id,
        source: rel.source,
        target: rel.target,
      },
    });
  }

  const metaboliteColor = '#259F64';
  const enzymeColor = '#C92F63';
  const textColor = '#363636';
  const lineColor = '#DBDBDB';

  const stylesheet = cytoscape.stylesheet()
    .selector('node')
    .css({
      content: 'data(name)',
      'font-size': '20px',
      'text-valign': 'top',
      'text-halign': 'center',
    })
    .selector('node[type="metabolite"]')
    .css({
      shape: 'elipse',
      'background-color': metaboliteColor,
      width: 15,
      height: 15,
      color: textColor,
    })
    .selector('node[type="enzyme"]')
    .css({
      shape: 'rectangle',
      'background-color': enzymeColor,
      width: 20,
      height: 20,
      color: textColor,
    })
    .selector('edge')
    .css({
      width: 3,
      'line-color': lineColor,
      'target-arrow-color': lineColor,
      'target-arrow-shape': 'triangle',
    })
    .selector(':selected')
    .css({
      'background-color': textColor,
      'line-color': textColor,
      'target-arrow-color': textColor,
      'source-arrow-color': textColor,
      'text-outline-color': textColor,
    });

  return [elmsjson, stylesheet];
}
