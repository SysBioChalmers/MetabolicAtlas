import cytoscape from 'cytoscape';

export default function (elms, rels, nodeDisplayParams) {
  const elmsjson = [];
  const enzExpSource = nodeDisplayParams.enzymeExpSource;
  const enzExpType = nodeDisplayParams.enzymeExpType;
  const enzSample = nodeDisplayParams.enzymeExpSample;

  // console.log(enzExpSource);
  // console.log(enzExpType);
  // console.log(enzSample);
  // console.log(nodeDisplayParams.enzymeNodeColor.hex);

  for (const id of Object.keys(elms)) {
    const elm = elms[id];

    if (elm.type === 'enzyme') {
      // let hpaLink = `http://www.proteinatlas.org/${elm.long}/`;
      if (enzExpSource && elm.expressionLvl) {
        if (nodeDisplayParams.enzymeExpSource === 'HPA') {
          // hpaLink = `http://www.proteinatlas.org/${elm.long}/nodeDisplayParams.enzymeExpSample#top`;
        }
      } else if (!elm.expressionLvl) {
        elm.expressionLvl = {};
        elm.expressionLvl.false = {};
        elm.expressionLvl.false.false = {};
        elm.expressionLvl.false.false.false = nodeDisplayParams.enzymeNodeColor.hex;
      } else {
        elm.expressionLvl.false.false.false = nodeDisplayParams.enzymeNodeColor.hex;
      }
      elmsjson.push({
        group: 'nodes',
        data: {
          id: elm.id,
          name: elm.name,
          color: elm.expressionLvl,
          // hpaLink, // TODO: move into config
          type: elm.type,
          // details: elm.details,
        },
      });
    } else {
      elmsjson.push({
        group: 'nodes',
        data: {
          id: elm.id,
          name: elm.name,
          type: elm.type,
          // details: elm.details,
        },
      });
    }
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
      'border-width': '1px',
      'border-color': 'black',
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
      shape: nodeDisplayParams.enzymeNodeShape,
      'background-color': function f(ele) {
        if (ele.data('color')[enzExpSource][enzExpType][enzSample]) {
          return ele.data('color')[enzExpSource][enzExpType][enzSample];
        }
        return 'whitesmoke';
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
