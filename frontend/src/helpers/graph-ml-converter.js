/* eslint-disable */
export default function (cyNetwork) {
    let graph = '<?xml version="1.0" encoding="UTF-8"?>\n' +
                  '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">' +
                 '\n\t<key attr.name="name" attr.type="string" for="node" id="name"/>' +
                 '\n\t<key attr.name="type" attr.type="string" for="node" id="type"/>' +
                 '\n\t<key attr.name="xpos" attr.type="int" for="node" id="xpos"/>' +
                 '\n\t<key attr.name="ypos" attr.type="int" for="node" id="ypos"/>' +
                 '\n\t<key attr.name="name" attr.type="string" for="edge" id="name"/>';
    graph += '\n\t<graph id=\"G\">';
    graph += appendNodes(cyNetwork.nodes());
    graph += appendEdges(cyNetwork.edges());
    graph += "\n\t</graph>\n</graphml>";
    return graph;

    function appendNodes(cyNodes) {
        let nodesString = '';
        cyNodes.forEach(function(ele){
            nodesString += `\n\t\t<node id="${ele.data().id}">`;
            nodesString += `\n\t\t\t<data key="name">${ele.data().name}</data>`;
            nodesString += `\n\t\t\t<data key="type">${ele.data().type}</data>`;
            nodesString += `\n\t\t\t<data key="xpos">${toInt(ele.position().x)}</data>`;
            nodesString += `\n\t\t\t<data key="ypos">${toInt(ele.position().y)}</data>`;
            nodesString += `\n\t\t</node>`;
        });
        return nodesString;
    }

    function appendEdges(cyEdges) {
        let edgesString = '';
        cyEdges.forEach(function(ele){
            edgesString += `\n\t\t<edge source="${ele.data().source}" target="${ele.data().target}">`;
            edgesString += `\n\t\t\t<data key="name">${ele.data().id}</data>`;
            edgesString += `\n\t\t</edge>`;
        });
        return edgesString;
    }

    function toInt(n) { return Math.round(Number(n)); };
};
