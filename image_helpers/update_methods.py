import xml.etree.ElementTree as ET
import libsbml

baseDir="/Users/halena/Documents/Sys2Bio/hma-prototype/frontend/src/assets/maps/compartment_level/"
sbmlVersion="{http://www.sbml.org/sbml/level3/version1/layout/version1}"
svgVersion="{http://www.w3.org/2000/svg}"

def readXML(xml_file):
    # https://docs.python.org/2/library/xml.etree.elementtree.html
    doc = ET.parse(xml_file)
    return(doc.getroot())

def readSBML(xml_file):
    doc = libsbml.readSBML(xml_file)
    return(doc)

def getAllSpeciesFromSBMLFile(xml_file):
    sbml = readXML(baseDir+xml_file)
    species = [] # multiple objects could theoretically end up at the same position...
    for lol in sbml.iter(sbmlVersion+'listOfLayouts'):
        for l in lol.iter(sbmlVersion+'layout'):
            for sg in l.findall(sbmlVersion+'listOfSpeciesGlyphs'):
                for s in sg.findall(sbmlVersion+'speciesGlyph'):
                    idOfSpecieGlyph = s.attrib[sbmlVersion+'species']
                    b = s.find(sbmlVersion+'boundingBox')
                    pos = b.find(sbmlVersion+'position')
                    dim = b.find(sbmlVersion+'dimensions')
                    positions = {}
                    positions['idOfSpecieGlyph'] = idOfSpecieGlyph
                    positions['id'] = re.sub(r'_[0-9]+$', '', idOfSpecieGlyph) # remove the last _[number] as this is just a count of where
                    positions['width'] = _truncate(dim.get(sbmlVersion+'width'))
                    positions['height'] = _truncate(dim.get(sbmlVersion+'height'))
                    x = _truncate(pos.get(sbmlVersion+'x')) # there is not an absolute exact match so skip the float part...
                    y = _truncate(pos.get(sbmlVersion+'y'))
                    #if(pos.get(sbmlVersion+'x')=="3829.7105224975785"):
                    #    print("X="+x+" Y="+y+" "+str(pos.attrib)+" -> ID "+idOfSpecieGlyph)
                    positions['x'] = x
                    positions['y'] = y
                    if(len(y)>0 and len(positions['height'])>0 and idOfSpecieGlyph.startswith("E")):
                        positions['yAdj'] = str(int(y)+int(positions['height']))
                    else:
                        positions['yAdj'] = y
                    if idOfSpecieGlyph.startswith("E"):
                        positions['type'] = "enzyme"
                    else:
                        positions['type'] = "metabolite"
                    species.append(positions)
                    #print("ID is "+id+" X="+x+" Y="+y+" W="+w+" H")
    return(species)

def _retrieveSpecies(list, x, y, attrib):
    foundCount=0
    found = None
    for cur in list:
        if cur['x'] == x and cur['yAdj'] == y:
            if foundCount > 0:
                print("previously found "+found['id']+" for position X="+x+" and Y="+y+" now found "+cur['id'])
                print("ATTRIBUTES are: "+str(attrib))
                found['id'] = "DUPLICATE"
                return(found)
            foundCount+=1
            found=cur
    if foundCount==0:
        print("No map found for "+x+" and "+y+" ATTRIBuTES were "+str(attrib))
    return(found)

def _truncate(number):
    return re.sub(r'\..*', '', number)

def updateSVGColor(compartmentName, svg_file, elementsToUpdate, newColor):
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    doc = ET.parse(baseDir+svg_file)
    svg = doc.getroot()
    gOuter = svg.find(svgVersion+'g')
    nonMapped=0
    for g in gOuter.findall(svgVersion+'g'):
        current = g.get('reaction_component_id')
        if current in elementsToUpdate:
            g.set('fill', newColor)
    doc.write(baseDir+compartmentName+'.colorSwapped.svg')


def updateSVGWithID(compartmentName, svg_file, sbmlSpecies, xAdjustENSG, yAdjustENSG, xAdjustMet, yAdjustMet):
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    doc = ET.parse(baseDir+svg_file)
    svg = doc.getroot()
    gOuter = svg.find(svgVersion+'g')
    nonMapped=0
    for g in gOuter.findall(svgVersion+'g'):
        transform = g.get('transform')
        temp = transform.split(',')
        x = float(temp[4])
        y = float(temp[5].replace(')',''))
        # handle the gene/protein/enzymes
        xSBML = _truncate(str(x + xAdjustENSG))
        ySBML = _truncate(str(y + yAdjustENSG))
        for textElement in g.findall(svgVersion+'text'):
            if textElement.text.startswith("ENSG"):
                found = _retrieveSpecies(sbmlSpecies, xSBML, ySBML, g.attrib)
                if not found is None:
                    g.set('reaction_component_id', found['id'])
                else:
                    nonMapped+=1
        # find the metabolites...
        fill = g.get('fill')
        if fill == "#a28dff":
            xSBML = _truncate(str(x + xAdjustMet))
            ySBML = _truncate(str(y + yAdjustMet))
            #print("in here with x="+str(x)+" and y="+str(y)+" adjusted -> "+xSBML+" "+ySBML)
            found = _retrieveSpecies(sbmlSpecies, xSBML, ySBML, g.attrib)
            if not found is None:
                g.set('reaction_component_id', found['id'])
            else:
                nonMapped+=1
    # write the new version of the SVG file with the identifiers...
    doc.write(baseDir+compartmentName+'.id_added.svg')
    print("A total of "+str(nonMapped)+" missing maps")
