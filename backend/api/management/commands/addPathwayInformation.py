###########################################################
### Go through all pathways and figure out X,Y for them ###
###########################################################

import sys, os, re

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand
from django.db import connection

padding = 500
svgFolder = "/project/svgs/"

# TODO consider also the position of the text of the pathway
def getMinAndMax(reactions):
    x_top_left = 100000
    y_top_left = 100000
    x_bottom_right = 0
    y_bottom_right = 0
    for r in reactions:
        x = r[0]
        y = r[1]
        if x < x_top_left:
            x_top_left = x
        if x > x_bottom_right:
            x_bottom_right = x
        if y < y_top_left:
            y_top_left = y
        if y > y_bottom_right:
            y_bottom_right = y

    return x_top_left, y_top_left, x_bottom_right, y_bottom_right



def readCompartment(fileName):
    """ Read svgs file and get all reactions ID and its coordinate x,y """
    ret = {}
    with open (svgFolder+fileName, "r") as myfile:
        data=myfile.readlines()
        for idx, l in enumerate(data):
            l = l.strip()
            if False and re.search("Shape_of_Reaction", l):
                # old version of svgs file
                rid = re.sub(r'^.*Shape_of_Reaction.','', l.rstrip())
                rid = re.sub(r'..$','', rid)
                trans = re.sub(r'^.*transform=.matrix.','', data[idx+1].rstrip())
                trans = re.sub(r'\W. .*','', trans)
                pos = trans.split(",")
                x = float(pos[4])
                y = float(pos[5])
                ret[rid] = (x, y)
            m = re.match('<g class="reaction" id="(.*)"', l)
            if m:
                rid = m.group(1)
                m = re.search('matrix[(]1,0,0,1,(\d+),(\d+)[)]', data[idx+1])
                x, y = m.groups()
                ret[rid] = (float(x), float(y))

    return ret

def compartmentByCompartment(ci, pathways, dict_pathway):
    m = readCompartment(ci.filename)
    print ("Reactions found in the SVG file: %s" % len(m))
    for p in pathways:
        reactions = SubsystemReaction.objects.filter(subsystem_id=p.id)
        if p.name not in dict_pathway:
            dict_pathway[p.name] = [len(reactions), {}]
        print ("Reactions found in '%s': %s" % (p.name, reactions.count()))
        r_overlap = [m[r.reaction_id] for r in reactions if r.reaction_id in m]
        print ("Overlap: %s (%s) " % (len(r_overlap), float(len(r_overlap))/len(reactions) * 100.0 ))
        dict_pathway[p.name][1][ci.display_name] = len(r_overlap)

        if r_overlap:
            # create tileSubtitle only if got coordinates
            box = getMinAndMax(r_overlap)
            # check if exists
            ss = Subsystem.objects.get(id=p.id)
            # TODO check if the pathway is really visible in the svg
            try:
                t = TileSubsystem.objects.get(subsystem_id=ss, compartment_name=ci.display_name)
                '''print ("Already exists")
                print (t.x_top_left, t.y_top_left, int(box[0]-padding), int(box[1]-padding))
                assert t.x_top_left == int(box[0]-padding)
                assert t.y_top_left == int(box[1]-padding)'''
            except TileSubsystem.DoesNotExist:
                t = TileSubsystem(subsystem_id = ss, subsystem_name=p.name,
                    compartmentinformation_id = ci.id,
                    compartment_name = ci.display_name,
                    x_top_left = box[0]-padding, y_top_left = box[1]-padding,
                    x_bottom_right = box[2]+padding, y_bottom_right = box[3]+padding,
                    reaction_count = len(r_overlap)) # store the real number of reaction in the compartment
                t.save()
        else:
            continue
            print ("Cannot get coord box for pathway %s" % p.name)
            exit(1)

    return dict_pathway

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
        print ("Make sure you put the last svg files version in data/svgs")
        input()
        pathways = Subsystem.objects.exclude(system='Collection of reactions')
        cis = CompartmentInformation.objects.all()
        dict_pathway = {}
        
        for ci in cis:
            print ("Processing compartement %s" % ci.display_name)
            dict_pathway = compartmentByCompartment(ci, pathways, dict_pathway)

        setAsMainIfInOnlyOneCompartment()
        manuallySetSomeAsMain()

        # check if the best compartment is selected as main, the one with the most of reactions
        for el, v in dict_pathway.items():
            most_present_compartment = [[k2, float(v[1][k2])/v[0] * 100] for k2 in sorted(v[1], key=v[1].get, reverse=True)][0]
            # print (el, v[0], sum([v2 for k2, v2 in v[1].items()]), most_present_compartment)
            dict_pathway[el].append(most_present_compartment)

        for sub in TileSubsystem.objects.filter(is_main=True):
            if dict_pathway[sub.subsystem_name][2][0] != sub.compartment_name:
                print ("Warning: '%s' main in '%s' but should be '%s'" % (sub.subsystem_name, sub.compartment_name, dict_pathway[sub.subsystem_name][2]))

