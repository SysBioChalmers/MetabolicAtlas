/* eslint-disable */

export default function (xmlText) {
    //Parse the xml source string into an XML Document
    var xmlDocSource = $.parseXML(xmlText);
    //wrap the xmlDocSource with jquery to use jquery suport for manipulating xml 
    var $xmlSource = $(xmlDocSource);

    //garphML has a very strict structure and rules so rather than creating a new xml document
    //and adding new nodes with JQuery it turned out much easier to just reformat the current nodes
    //and add them to a new body.  Otherwise I got all sorts of problems with the domians (xmlns).
    //this is only true when parsing XML.
    cleanGraphmlSource($xmlSource);

    //create a new valid root graphml document 
    var xmlDocTarget = createCompatibleGraphmlRoot();
    var $xmlTarget = $(xmlDocTarget);

    //inject the cleaned nodes to the new compatible document
    injectCleanGraphToGraphMlRoot($xmlSource, $xmlTarget);

    //convert teh xml document to string
    var output = xmlToString(xmlDocTarget);
    return output;

    //private functions
    function cleanGraphmlSource(xml) {
        function isWantedCssAttribute(value) {
            if (value === "shape") return true;
            if (value === "backgroundColor") return true;
            return false;
        }
        function renameWantedCssAttribute(value) {
            if (value === "shape") return "Shape";
            if (value === "backgroundColor") return "Color";
            return "";
        }
        //get all nodes 
        var $nodes = xml.find("node");
        $nodes.each(function () {
            //In all cases the type attibute is invalid and must be removed
            //when a node is of type ccc clean using this logic
            var $datumCss = $(this).find("data[type='css']");
            $datumCss.each(function () {
                var key = $(this).attr("key");
                $(this).removeAttr("type");
                //if key is not in wanted list, remove, if it is rename it
                //NOTE: the key attibute here MUST match the KEY attibute on the createCompatibleGraphmlRoot() function
                if (isWantedCssAttribute(key)) {
                    var renamedAttribute = renameWantedCssAttribute(key);
                    $(this).attr({ key: renamedAttribute });
                } else
                    $(this).remove();

            });
            //when a node is of type data clean using this logic
            var $datumData = $(this).find("data[type='data']");
            $datumData.each(function () {
                $(this).removeAttr("type");
            });
            //when a node is of type data clean using this logic
            var $datumPosition = $(this).find("data[type='position']");
            $datumPosition.each(function () {
                $(this).removeAttr("type");
            });
        });
    }
    function createCompatibleGraphmlRoot() {
        //here all the attibutes MUST be declared as <key> elements
        var xmlDocTarget = $.parseXML(
            '<?xml version="1.0" encoding="UTF-8"?>\n' +
            '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"\n' +
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n' +
            'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns\n' +
            'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n' +
            '<key attr.name="name" attr.type="string" for="node" id="name"/>\n' +
            '<key attr.name="hpaLink" attr.type="string" for="node" id="hpaLink"/>\n' +
            '<key attr.name="type" attr.type="string" for="node" id="type"/>\n' +
            '<key attr.name="details" attr.type="string" for="node" id="details"/>\n' +
            '<key attr.name="x" attr.type="long" for="node" id="x"/>\n' +
            '<key attr.name="y" attr.type="long" for="node" id="y"/>\n' +
            '<key attr.name="Shape" attr.type="string" for="node" id="Shape"/>\n' +
            '<key attr.name="Color" attr.type="string" for="node" id="Color" />\n' +
            ' </graphml>\n'
        );
        return xmlDocTarget;
    };
    function injectCleanGraphToGraphMlRoot(source, target) {
        var $graphmlSource = target.find("graphml");
        var $graphSource = source.find("graph");
        $graphSource.appendTo($graphmlSource);
    }
    function xmlToString(xmlData) {

        var xmlString;
        if (window.ActiveXObject) {
            xmlString = xmlData.xml;
        }
        else {
            xmlString = (new XMLSerializer()).serializeToString(xmlData);
        }
        return xmlString;
    }
};
