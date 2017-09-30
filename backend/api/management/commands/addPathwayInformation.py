###########################################################
### Go through all pathways and figure out X,Y for them ###
###########################################################

import sys, os, re

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand
from django.db import connection

padding = 500
svgFolder = "../nginx/svgs/"


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
    with open (svgFolder+fileName, "r") as myfile:
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

def compartmentByCompartment(ci, pathways):
    m = readCompartment(ci.filename)
    for p in pathways:
        reactions = SubsystemReaction.objects.filter(subsystem_id=p.id)
        box = getMinAndMax(reactions, m)
        if( not box is None ):
            t = TileSubsystem(subsystem_id = p.id, subsystem_name=p.name,
                compartmentinformation_id = ci.id,
                compartment_name = ci.display_name,
                x_top_left = box[0]-padding, y_top_left = box[1]-padding,
                x_bottom_right = box[2]+padding, y_bottom_right = box[3]+padding,
                reaction_count = len(reactions) )
            t.save()

def setAsMainIfInOnlyOneCompartment():
    sql = "update tile_subsystems set is_main=true where subsystem_id in (select subsystem_id from tile_subsystems group by subsystem_id having count(*)<2);"
    with connection.cursor() as cursor:
        cursor.execute(sql)

def manuallySetSomeAsMain():
    t = TileSubsystem.objects.filter(
        subsystem_name="Tricarboxylic acid cycle and glyoxylate/dicarboxylate metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Starch and sucrose metabolism",
        compartment_name="Lysosome").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Pentose and glucuronate interconversions",
        compartment_name="ER").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Pyruvate metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Pentose phosphate pathway",
        compartment_name="ER").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Histidine metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Tryptophan metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Tyrosine metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Valine, leucine, and isoleucine metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Glutathione metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="beta-Alanine metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="O-glycan metabolism",
        compartment_name="Golgi").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Sulfur metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Linoleate metabolism",
        compartment_name="ER").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Eicosanoid metabolism",
        compartment_name="ER").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Carnitine shuttle (endoplasmic reticular)",
        compartment_name="ER").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Acylglycerides metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Beta oxidation of phytanic acid (peroxisomal)",
        compartment_name="Peroxisome").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Beta oxidation of unsaturated fatty acids (n-7) (mitochondrial)",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Terpenoid backbone biosynthesis",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Androgen metabolism",
        compartment_name="ER").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Glycosphingolipid biosynthesis-globo series",
        compartment_name="Lysosome").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Glycosylphosphatidylinositol (GPI)-anchor biosynthesis",
        compartment_name="ER").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Prostaglandin biosynthesis",
        compartment_name="ER").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Ether lipid metabolism",
        compartment_name="Peroxisome").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Bile acid recycling",
        compartment_name="ER").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Biopterin metabolism",
        compartment_name="Nucleus").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Ascorbate and aldarate metabolism",
        compartment_name="ER").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Porphyrin metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Retinol metabolism",
        compartment_name="ER").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Thiamine metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Vitamin B12 metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Vitamin D metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Vitamin E metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Metabolism of xenobiotics by cytochrome P450",
        compartment_name="ER").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Fatty acid biosynthesis (even-chain)",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Fatty acid transfer reactions",
        compartment_name="Peroxisome").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Acyl-CoA hydrolysis",
        compartment_name="Peroxisome").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Beta oxidation of unsaturated fatty acids (n-7) (mitochondrial)",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.filter(
        subsystem_name="Biotin metabolism",
        compartment_name="Nucleus").update(is_main=True)
    #t = TileSubsystem.objects.filter(
    #    subsystem_name="",
    #    compartment_name="").update(is_main=True)


class Command(BaseCommand):

    def handle(self, *args, **options):
        pathways = Subsystem.objects.exclude(system='Collection of reactions')
        cis = CompartmentInformation.objects.all()
        for ci in cis:
            compartmentByCompartment(ci, pathways)
        setAsMainIfInOnlyOneCompartment()
        manuallySetSomeAsMain()
