import re, sys, os, argparse
import xml.etree.ElementTree as ET

import update_methods as um


solita="solita/" # sym link since I cant get the spaces to work...
sbmlVersion="{http://www.sbml.org/sbml/level3/version1/layout/version1}"

parser = argparse.ArgumentParser()
parser.add_argument('--addID', action='store_true', default=False);
parser.add_argument('--changeColorFor', type=str, default=None);
parser.add_argument('--changeColorTo', type=str, default=None);
parser.add_argument('-v', dest='verbose', action='store_true', default=False);
args = parser.parse_args()


if(args.addID):
    # ER
    sbml = um.getAllSpeciesFromSBMLFile(solita+'ER.sbml')
    um.updateSVGWithID("ER", "ER.svg.fixed.svg.unique.svg", sbml, -67.4, -5073, -67.4, -5073)
    # nucleosome
    #sbml = um.getAllSpeciesFromSBMLFile(solita+'nucleosome.sbml')
    #um.updateSVGWithID("nucleosome", "nucleosome.svg.fixed.svg.unique.svg", sbml, -10668, -61, -10668, -61)
elif(not args.changeColorFor is None):
    hardCoded={}
    hardCoded['M_m03130n']=1
    hardCoded['M_m02750n']=1
    hardCoded['M_m00204n']=1
    um.updateSVGColor("nucleosome", "nucleosome.id_added.svg", hardCoded, "#8aff33")
else:
    # fix the perixome so that the right version also has a id...
    ET.register_namespace('', "http://www.sbml.org/sbml/level3/version1/groups/version1")
    # read in the original imported XML file...
    doc = ET.parse('/Users/halena/Documents/Sys2Bio/2016/models/bin/compartmentP.xml')
    root = doc.getroot()
    #for child in root.iter():
    #    print(child.tag)
    maps = {}
    for s in root.iter('{http://www.sbml.org/sbml/level3/version1/core}species'):
        maps[s.get('name')] = s.get('id')
        #print("NAME is "+s.get('name'))
    # read in the exported SBML file
    ET.register_namespace('', "http://www.sbml.org/sbml/level3/version1/core")
    doc = ET.parse(solita+'perixome.sbml')
    root = doc.getroot()
    for s in root.iter('{http://www.sbml.org/sbml/level3/version1/core}species'):
        if s.get('name') in maps:
            s.set('id', maps[s.get('name')])
        else:
            print("Missing name "+s.get('name'))
    doc.write('test.xml')
