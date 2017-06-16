import cytoscape from 'cytoscape';

export default function (elms, rels, nodeDisplayParams) {
  const elmsjson = [];
  const tissue = nodeDisplayParams.activeTissue;

  for (const id of Object.keys(elms)) {
    const elm = elms[id];
    elm.tissue_expression.false = nodeDisplayParams.enzymeNodeColor.hex;
    elmsjson.push({
      group: 'nodes',
      data: {
        id: elm.id,
        name: elm.short,
        expression_color: elm.tissue_expression,
        hpaLink: `http://www.proteinatlas.org/${elm.long}/tissue#top`, // TODO: move into config
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

  const metaboliteColor = nodeDisplayParams.metaboliteNodeColor.hex;
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
      // shape: 'elipse',
      shape: nodeDisplayParams.metaboliteNodeShape,
      'background-color': metaboliteColor,
      width: 15,
      height: 15,
      color: textColor,
    })
    .selector('node[type="enzyme"]')
    .css({
      // shape: 'rectangle',
      shape: nodeDisplayParams.enzymeNodeShape,
      'background-color': function (ele) {
        if (ele.data('expression_color')[tissue]) {
          return ele.data('expression_color')[tissue];
        }
        return 'grey';
      },
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
    })
    .selector('core')
    .css({
      'active-bg-color': '#64CC9A',
      'active-bg-opacity': 0.25,
      'active-bg-size': 10,
    });

  return [elmsjson, stylesheet];
}
