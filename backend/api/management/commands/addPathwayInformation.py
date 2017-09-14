###########################################################
### Go through all pathways and figure out X,Y for them ###
###########################################################

import sys, os, re

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand

padding = 500


def getMinAndMax(reactions, allPos):
    x_top_left = 100000
    y_top_left = 100000
    x_bottom_right = 0
    y_bottom_right = 0
    comps = {}
    for r in reactions:
        if( r.reaction_id in allPos ):
            pos = allPos[r.reaction_id]
            x = pos[0]
            y = pos[1]
            comps[r.reaction.compartment] = "1"
            if( x < x_top_left ):
                x_top_left = x
            if( x > x_bottom_right ):
                x_bottom_right = x
            if( y < y_top_left ):
                y_top_left = y
            if( y > y_bottom_right ):
                y_bottom_right = y
    if(len(comps)>0):
        return(x_top_left, y_top_left, x_bottom_right, y_bottom_right, comps)
    else:
        return(None)



def readCompartment(fileName):
    ret = {}
    with open (fileName, "r") as myfile:
        data=myfile.readlines()
        for idx, l in enumerate(data):
            if( re.search("Shape_of_Reaction", l) ):
                rid = re.sub(r'^.*Shape_of_Reaction.','', l.rstrip())
                rid = re.sub(r'..$','', rid)
                trans = re.sub(r'^.*transform=.matrix.','', data[idx+1].rstrip())
                trans = re.sub(r'\W. .*','', trans)
                pos = trans.split(",")
                x = float(pos[4])
                y = float(pos[5])
                ret[rid] = (x, y)
    return(ret)

def compartmentByCompartment(fileName, compName, pathways):
    m = readCompartment(fileName)
    for p in pathways:
        reactions = SubsystemReaction.objects.filter(subsystem_id=p.id)
        box = getMinAndMax(reactions, m)
        if( not box is None ):
            t = TileSubsystem(subsystem_id = p.id, subsystem_name=p.name,
                compartment_name = compName, x_top_left = box[0]-padding,
                y_top_left = box[1]-padding, x_bottom_right = box[2]+padding,
                y_bottom_right = box[3]+padding,
                reaction_count = len(reactions) )
            t.save()

def goThroughTheSVGFilesAndAddBoxInformation():
    pathways = Subsystem.objects.exclude(system='Collection of reactions')

    svg = "../nginx/svgs/ER.svg"
    compartmentByCompartment(svg, "ER", pathways)
    svg = "../nginx/svgs/golgi.svg"
    compartmentByCompartment(svg, "Golgi", pathways)
    svg = "../nginx/svgs/lysosome.svg"
    compartmentByCompartment(svg, "Lysosome", pathways)
    svg = "../nginx/svgs/mitochondrion_old.svg"
    compartmentByCompartment(svg, "Mitochondria", pathways)
    svg = "../nginx/svgs/nucleus.svg"
    compartmentByCompartment(svg, "Nucleus", pathways)
    svg = "../nginx/svgs/peroxisome.svg"
    compartmentByCompartment(svg, "Peroxisome", pathways)
    # then do the cytosol groups
    svg = "../nginx/svgs/cytosol_1.svg"
    compartmentByCompartment(svg, "Cytosol_1", pathways)
    svg = "../nginx/svgs/cytosol_2.svg"
    compartmentByCompartment(svg, "Cytosol_2", pathways)
    svg = "../nginx/svgs/cytosol_3.svg"
    compartmentByCompartment(svg, "Cytosol_3", pathways)
    svg = "../nginx/svgs/cytosol_4.svg"
    compartmentByCompartment(svg, "Cytosol_4", pathways)
    svg = "../nginx/svgs/cytosol_5.svg"
    compartmentByCompartment(svg, "Cytosol_5", pathways)
    svg = "../nginx/svgs/cytosol_6.svg"
    compartmentByCompartment(svg, "Cytosol_6", pathways)


def manuallySetSomeAsMain():
    t = TileSubsystem.objects.filter(
        subsystem_name="Tricarboxylic acid cycle and glyoxylate/dicarboxylate metabolism",
        compartment_name="Mitochondria").update(is_main=True)


class Command(BaseCommand):

    def handle(self, *args, **options):
        goThroughTheSVGFilesAndAddBoxInformation()
        manuallySetSomeAsMain()
