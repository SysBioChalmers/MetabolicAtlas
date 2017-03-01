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
        type: elm.type,
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
      'background-color': '#00ff00',
      width: 15,
      height: 15,
      color: '#000000',
    })
    .selector('node[type="enzyme"]')
    .css({
      shape: 'rectangle',
      'background-color': '#ff0000',
      width: 20,
      height: 20,
      color: '#000000',
    })
    .selector('edge')
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
