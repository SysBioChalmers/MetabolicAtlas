import createGraph from 'ngraph.graph';
import createLayout from 'ngraph.forcelayout';

const SCALE = 5;
const MAX_ITERATIONS = 1000;

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

  const startTime = Date.now();
  const layout = createLayout(g, { dimensions: 3 });

  let iterations = MAX_ITERATIONS;
  const elementsCount = nodes.length + links.length;
  if (elementsCount > 50000) {
    // From benchmarks, it takes about 60s to run 300 iterations
    // for a network of around 60000 elements (nodes + links) 
    // so the iterations is capped at 200 for optimal speed
    iterations = 200;
  } else if (elementsCount > 12000) {
    // From benchmarks, it takes about 25s and 800 iterations
    // to stabilize a network of around 11000 elements (nodes + links) 
    // so the iterations is capped at 800 for optimal quality
    iterations = 800;
  }

  for (let i = 1; i <= iterations; ++i) {
    const isStable = layout.step();

    if (isStable) {
      break;
    }
  }

  const nodesWithPos = [];

  g.forEachNode((node) => {
    const { x, y, z } = layout.getNodePosition(node.id);
    const pos = [
      Math.round(x * SCALE),
      Math.round(y * SCALE),
      Math.round(z * SCALE),
    ];

    nodesWithPos.push({
      id: node.id,
      pos,
      ...node.data,
    });
  });

  return {
    nodes: nodesWithPos,
    links,
  };
};

export default populateWithLayout;
