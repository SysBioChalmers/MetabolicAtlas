import re, sys, os, argparse

import update_methods as um


solita="solita/" # sym link since I cant get the spaces to work...

parser = argparse.ArgumentParser()
parser.add_argument('--addID', action='store_true', default=False);
parser.add_argument('--changeColorFor', type=str, default=None);
parser.add_argument('--changeColorTo', type=str, default=None);
parser.add_argument('-v', dest='verbose', action='store_true', default=False);
args = parser.parse_args()


if(args.addID):
    # ER
    #sbml = getAllSpeciesFromSBMLFile(solita+'ER.sbml')
    #updateSVGWithID("ER", baseDir+"ER.svg.fixed.svg.unique.svg", sbml, -567.4, -5020.465, -651.808288, -5073.4495)
    # nucleosome
    sbml = getAllSpeciesFromSBMLFile(solita+'nucleosome.sbml')
    updateSVGWithID("nucleosome", "nucleosome.svg.fixed.svg.unique.svg", sbml, -10640, -48, -10668, -61)
elif(not args.changeColorFor is None):
    hardCoded={}
    hardCoded['M_m03130n']=1
    hardCoded['M_m02750n']=1
    hardCoded['M_m00204n']=1
    um.updateSVGColor("nucleosome", "nucleosome.id_added.svg", hardCoded, "#8aff33")
