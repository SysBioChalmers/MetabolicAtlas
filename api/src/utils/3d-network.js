import createGraph from 'ngraph.graph';
import createLayout from 'ngraph.forcelayout';

const populateWithLayout = ({ nodes, links }) => {
  const g = createGraph();

  for (let node of nodes) {
    const { id, ...data } = node;
    g.addNode(id, data);
  }

  for (let link of links) {
    const { s, t } = link;
    g.addLink(s, t);
  }

  const layout = createLayout(g, { dimensions: 3 });

  for (let i = 0; i < 100; ++i) {
    layout.step();
  }

  const nodeSet = new Set();
  const linkSet = new Set();

  g.forEachNode((node) => {
    const { x, y, z } = layout.getNodePosition(node.id);
    const pos = [
      Math.round(x * 5),
      Math.round(y * 5),
      Math.round(z * 5),
    ];

    nodeSet.add({
      id: node.id,
      pos,
      ...node.data,
    });

    for (let link of node.links) {
      linkSet.add({ s: link.fromId, t: link.toId });
    }
  });

  return {
    nodes: [...nodeSet],
    links: [...linkSet],
  };
};

export default populateWithLayout;
