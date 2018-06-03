import cytoscape from 'cytoscape';

export default function (
  componentID, elms, rels, nodeDisplayParams, reactionHL, compartmentHL, subsystemHL) {
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
          reaction: elm.reaction,
          compartment: elm.compartment,
          subsystem: elm.subsystem,
          type: elm.type,
        },
      });
    } else {
      elmsjson.push({
        group: 'nodes',
        data: {
          id: elm.id,
          name: elm.name,
          type: elm.type,
          reaction: elm.reaction,
          compartment: elm.compartment,
          subsystem: elm.subsystem,
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
        order: rel.order,
        reaction: rel.reaction,
        direction: rel.direction,
      },
    });
  }

  const metaboliteColor = nodeDisplayParams.metaboliteNodeColor.hex;
  const textColor = '#363636';
  const textColorHL = '#CC3636';
  const textColorHLpartial = '#f4ad42';
  const lineColor = '#bbbbbb';
  // const expLineColor = '#bbbbbb';

  const stylesheet = cytoscape.stylesheet()
    .selector('node')
    .css({
      content: 'data(name)',
      'font-size': '20px',
      'font-weight': function f(e) {
        if (reactionHL && e.data().reaction && e.data().reaction.has(reactionHL)) {
          return 'bold';
        } else if (!reactionHL) {
          return 'normal';
        }
        return 'normal';
      },
      'text-valign': 'top',
      'text-halign': 'center',
      'border-width': '1px',
      'border-color': function f(e) {
        if (e.data().id === componentID) {
          return 'white';
        }
        return 'black';
      },
    })
    .selector('node[type="metabolite"]')
    .css({
      shape: nodeDisplayParams.metaboliteNodeShape,
      'background-color': metaboliteColor,
      width: 15,
      height: 15,
      color: function f(e) {
        if (compartmentHL && subsystemHL) {
          if (e.data().compartment === compartmentHL && e.data().subsystem.has(subsystemHL)) {
            return textColorHL;
          }
        } else if (compartmentHL && e.data().compartment === compartmentHL) {
          return textColorHL;
        } else if (subsystemHL && e.data().subsystem.has(subsystemHL)) {
          return textColorHL;
        }
        return textColor;
      },
      opacity: function f(e) {
        if (reactionHL && e.data().reaction && e.data().reaction.has(reactionHL)) {
          return 1;
        } else if (!reactionHL) {
          return 1;
        }
        return 0.6;
      },
    })
    .selector('node[type="enzyme"]')
    .css({
      shape: nodeDisplayParams.enzymeNodeShape,
      'background-color': function f(e) {
        if (e.data('color')[enzExpSource][enzExpType][enzSample]) {
          return e.data('color')[enzExpSource][enzExpType][enzSample];
        }
        return 'whitesmoke';
      },
      width: 20,
      height: 20,
      color: function f(e) {
        if (compartmentHL && subsystemHL) {
          if (compartmentHL in e.data().compartment && e.data().subsystem.has(subsystemHL)) {
            if (e.data().compartment[compartmentHL] === 0) {
              return textColorHLpartial;
            }
            return textColorHL;
          }
        } else if (compartmentHL && compartmentHL in e.data().compartment) {
          if (e.data().compartment[compartmentHL] === 0) {
            return textColorHLpartial;
          }
          return textColorHL;
        } else if (subsystemHL && e.data().subsystem.has(subsystemHL)) {
          return textColorHL;
        }
        return textColor;
      },
      opacity: function f(e) {
        if (reactionHL && e.data().reaction && e.data().reaction.has(reactionHL)) {
          return 1;
        } else if (!reactionHL) {
          return 1;
        }
        return 0.6;
      },
    })
    .selector('edge')
    .css({
      width: 1,
      'arrow-scale': 0.35,
      opacity: function f(e) {
        if (reactionHL && e.data().reaction && e.data().reaction.has(reactionHL)) {
          return 1;
        } else if (!reactionHL) {
          return 1;
        }
        return 0.2;
      },
      'line-color': lineColor,
      'line-style': function f(e) {
        if (e.data('order') !== 1) {
          return 'dashed';
        }
        return 'solid';
      },
      'mid-target-arrow-color': '#723b00',
      'mid-target-arrow-shape': function f(e) {
        if (e.data().direction && reactionHL in e.data().direction) {
          if (e.data().direction[reactionHL] === 1) {
            return 'triangle-tee';
          } else if (e.data().direction[reactionHL] === 0) {
            return 'diamond';
          }
          return 'none';
        }
        return 'none';
      },
      'mid-source-arrow-color': '#723b00',
      'mid-source-arrow-shape': function f(e) {
        if (e.data().direction && reactionHL in e.data().direction) {
          if (e.data().direction[reactionHL] === -1) {
            return 'triangle-tee';
          } else if (e.data().direction[reactionHL] === 0) {
            return 'diamond';
          }
          return 'none';
        }
        return 'none';
      },
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
