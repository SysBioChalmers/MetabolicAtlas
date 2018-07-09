###########################################################
### Go through all pathways and figure out X,Y for them ###
###########################################################
import csv
import os
import re
import operator

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand
from django.db import connection
from django.db import connections
from django.db.models import Q

padding = 500
svgFolder = "/project/svgs/"

# TODO consider also the position of the text of the pathway
# but fix the svg first
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

    return x_top_left-padding, y_top_left-padding, x_bottom_right+padding, y_bottom_right+padding


def read_compartment_reaction(fileName):
    """ Read svgs file and get all reactions ID and its coordinate x,y """
    res = {}
    with open(os.path.join(svgFolder, fileName), "r") as myfile:
        data = myfile.readlines()
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
                res[rid] = (x, y)
            m = re.match('<g class="reaction" id="([^"]+)"', l)
            if m:
                rid = m.group(1)
                # FIX ME, might need to change 1 to 1.0 
                m = re.search('matrix[(]1[.]0,0,0,1[.]0,(\d+(?:[.]\d+)?),(\d+(?:[.]\d+)?)[)]', data[idx+1])
                x, y = m.groups()
                res[rid] = (float(x), float(y))
    return res

def read_compartment_subsystem_text(filename, subsystem_name):
    # TODO get the coordinate of the text of the pathway name
    # to get a better TileSubsystem coordinate
    pass


def read_compartment_metabolite(fileName):
    res = {}
    with open(os.path.join(svgFolder, fileName), "r") as myfile:
        data = myfile.readlines()
        for idx, l in enumerate(data):
            l = l.strip()
            m = re.match('<g class="metabolite" id="(m[^"]+)"', l)
            if m:
                rid = m.group(1).split('-')[0]
                res[rid] = None

    return res


def read_compartment_multi_metabolite(fileName):
    res = set()
    unique = set()
    with open(os.path.join(svgFolder, fileName), "r") as myfile:
        data = myfile.readlines()
        for idx, l in enumerate(data):
            l = l.strip()
            m = re.match('<g class="metabolite" id="(m[^"]+)"', l)
            if m:
                rid = m.group(1).split('-')[0]
                if rid in unique:
                    res.add(rid)
                unique.add(rid)

    return res

def read_compartment_enzyme(fileName):
    res = {}
    with open(os.path.join(svgFolder, fileName), "r") as myfile:
        data = myfile.readlines()
        for idx, l in enumerate(data):
            l = l.strip()
            m = re.match('<g class="metabolite" id="(ENSG[^"]+)"', l)
            if m:
                rid = m.group(1).split('-')[0]
                res[rid] = None

    return res


def get_real_subsystem_name(database, name_svg, fileName):
    name_svg = re.sub('^pathway[_]', '', name_svg)
    s = Subsystem.objects.using(database).filter(
        name__iregex='^' + name_svg.replace('_', '.{1,3}'))
    if not s or s.count() > 1:
        print ('^' + name_svg.replace('_', '.{1,3}'))
        print ('-' + name_svg + '-')
        print (name_svg)
        print (fileName)
        if not s:
            print ("not found")
        elif s.count() > 1:
            print ([s2.name for s2 in s])
            print ("too many")
        exit(1)
    return s[0].name


def read_compartment_subsystem(database, fileName):
    res = {}
    with open(os.path.join(svgFolder, fileName), "r") as myfile:
        data = myfile.readlines()
        for idx, l in enumerate(data):
            l = l.strip()
            m = re.match('<g class="pathway" id="([^"]+)"', l)
            if m:
                sid = m.group(1)
                sid = get_real_subsystem_name(database, sid, fileName)
                res[sid] = None

    return res


def reformat_pw_name(pw_name):
    pw_name = pw_name.replace(' ', '_').replace(',', '_'). \
        replace('/', '_').replace('-', '_').replace('(', '_'). \
        replace(')', '_')
    #pw_name = re.sub('_{2,}', '_', pw_name)
    #return pw_name.strip('_')
    return pw_name


def is_compartment_pathway(fileName, pathway):
    res = {}
    with open(os.path.join(svgFolder, fileName), "r") as myfile:
        data = myfile.readlines()
        for idx, l in enumerate(data):
            l = l.strip()
            pw_name = reformat_pw_name(pathway)
            # print (pw_name)
            m = re.match('<g class="pathway" id="pathway_%s">' % \
                pw_name, l)
            if m:
                return pw_name

    return False


def readPathwayTitle(fileName):
    with open(os.path.join(svgFolder, fileName), "r") as myfile:
        data = myfile.readlines()
        for idx, l in enumerate(data):
            l = l.strip()


def setAsMainIfInOnlyOneCompartment(database):
    # TODO check the result, the table was not updated the last time this code ran
    # expected ~37 uptaded rows
    sql = ("update tile_subsystems "
                "set is_main = true" 
                " where subsystem_id in ("
                    "select subsystem_id from tile_subsystems group by subsystem_id having count(*) = 1"
                ")")
    with connections[database].cursor() as cursor:
        cursor.execute(sql)


def manuallySetSomeAsMain(database):
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Tricarboxylic acid cycle and glyoxylate/dicarboxylate metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Starch and sucrose metabolism",
        compartment_name="Lysosome").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Pentose and glucuronate interconversions",
        compartment_name="Endoplasmic reticulum").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Pyruvate metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Pentose phosphate pathway",
        compartment_name="Endoplasmic reticulum").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Histidine metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Tryptophan metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Tyrosine metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Valine, leucine, and isoleucine metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Glutathione metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="beta-Alanine metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="O-glycan metabolism",
        compartment_name="Golgi").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Sulfur metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Linoleate metabolism",
        compartment_name="Endoplasmic reticulum").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Eicosanoid metabolism",
        compartment_name="Endoplasmic reticulum").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Carnitine shuttle (endoplasmic reticular)",
        compartment_name="Endoplasmic reticulum").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Acylglycerides metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Beta oxidation of phytanic acid (peroxisomal)",
        compartment_name="Peroxisome").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Beta oxidation of unsaturated fatty acids (n-7) (mitochondrial)",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Terpenoid backbone biosynthesis",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Androgen metabolism",
        compartment_name="Endoplasmic reticulum").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Glycosphingolipid biosynthesis-globo series",
        compartment_name="Lysosome").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Glycosylphosphatidylinositol (GPI)-anchor biosynthesis",
        compartment_name="Endoplasmic reticulum").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Prostaglandin biosynthesis",
        compartment_name="Endoplasmic reticulum").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Ether lipid metabolism",
        compartment_name="Peroxisome").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Bile acid recycling",
        compartment_name="Endoplasmic reticulum").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Biopterin metabolism",
        compartment_name="Nucleus").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Ascorbate and aldarate metabolism",
        compartment_name="Endoplasmic reticulum").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Porphyrin metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Retinol metabolism",
        compartment_name="Endoplasmic reticulum").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Thiamine metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Vitamin B12 metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Vitamin D metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Vitamin E metabolism",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Metabolism of xenobiotics by cytochrome P450",
        compartment_name="Endoplasmic reticulum").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Fatty acid biosynthesis (even-chain)",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Fatty acid transfer reactions",
        compartment_name="Peroxisome").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Acyl-CoA hydrolysis",
        compartment_name="Peroxisome").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Beta oxidation of unsaturated fatty acids (n-7) (mitochondrial)",
        compartment_name="Mitochondria").update(is_main=True)
    t = TileSubsystem.objects.using(database).filter(
        subsystem_name="Biotin metabolism",
        compartment_name="Nucleus").update(is_main=True)
    #t = TileSubsystem.objects.using(database).filter(
    #    subsystem_name="",
    #    compartment_name="").update(is_main=True)


def autoSetIsMain(database, pathway_compt_coverage):
    # check if the best compartment is selected as main, the one with the most of reactions
    for el, v in pathway_compt_coverage.items():
        most_present_compartment = [[k2, float(v[1][k2])/v[0] * 100] for k2 in sorted(v[1], key=v[1].get, reverse=True)][0:2]
        # print (el, v[0], sum([v2 for k2, v2 in v[1].items()]), most_present_compartment)
        pathway_compt_coverage[el].append(most_present_compartment)
        # print(most_present_compartment[0])
        # print (pathway_compt_coverage[el])
        # exit(1)

    for sub in TileSubsystem.objects.using(database).filter(is_main=True):
        if pathway_compt_coverage[sub.subsystem_name][2][0][0] != sub.compartment_name:
            print ("Warning: '%s' main in '%s' but should be '%s'" % (sub.subsystem_name, sub.compartment_name, pathway_compt_coverage[sub.subsystem_name][2]))


    s_ismain = 0
    s_no_ismain = 0
    for el, v in pathway_compt_coverage.items():
        most_compart, perc = v[2][0]
        if perc > 60.0: # FIX ME auto main if contains 60% of all the reactions
            ts = TileSubsystem.objects.using(database).filter(subsystem_name=el).update(is_main=False)
            s_ismain += TileSubsystem.objects.using(database).filter(subsystem_name=el, compartment_name=most_compart).update(is_main=True)


    # select subsystem without is_main set
    s_main = TileSubsystem.objects.using(database).filter(is_main=True).values_list('subsystem_name', flat=True)
    s_no_ismain = TileSubsystem.objects.using(database).filter(~Q(subsystem_name__in=s_main))

    print ("Subsystems with main compartment:", s_ismain)
    print ("Subsystems without main compartment:", len(s_no_ismain))
    print ("total TileSubsystem:", len(TileSubsystem.objects.using(database).all()))

    for el in s_no_ismain:
        print (pathway_compt_coverage[el.subsystem_name][2])


def write_subsystem_summary_file(database, rme_compt_svg, sub_compt_svg, pathway_compt_coverage):
    # read the subsystem from db to get the system and keep the same order
    subsystems = Subsystem.objects.using(database).all()
    subsystems = sorted(subsystems, key=operator.attrgetter('name'))

    cor = []
    with open("database_generation/connectivity/subsystem.txt", 'w') as fw:
        for ss in subsystems:
            sorted_dict = sorted(pathway_compt_coverage[ss.name][1].items(), key=operator.itemgetter(1), reverse=True)
            percent_reaction_db = "; ".join(["%s:%s" % (k, v) for (k, v) in sorted_dict])

            is_main = []
            if ss.name in sub_compt_svg:
                compartment_from_svg = "; ".join(sub_compt_svg[ss.name])
                for compt in sub_compt_svg[ss.name]:
                    r = TileSubsystem.objects.using(database).filter(subsystem_name=ss.name, compartment_name__iregex=compt+'.*')
                    if r:
                        # print (len(r))
                        r = r[0]
                        # print (r.subsystem_name, r.compartment_name, r.is_main)
                        is_main.append(str(r.is_main))
                    else:
                        # print ("error", ss.name, compt)
                        is_main.append("None")
                        # exit()
            else:
                compartment_from_svg = ''

            if ss.system != 'Collection of reactions':
                fw.write("%s\t%s\t%s\t%s\t%s\n" % (ss.name, ss.system, percent_reaction_db, compartment_from_svg, "; ".join(is_main)))
            else:
                cor.append("%s\t%s\t%s\t%s\t%s\n" % (ss.name, ss.system, percent_reaction_db, compartment_from_svg, "; ".join(is_main)))

        for line in cor:
            fw.write(line)

        # exit()


def write_ssub_connection_files(database, v):
    with open('database_generation/%s/output/subs_connect_mat.txt' % database, 'w') as fw:
        ssubs = list(v.keys())
        fw.write("#\t" + "\t".join(ssubs) + "\n")
        for ssub1 in ssubs:
            fw.write("%s\t" % ssub1)
            for ssub2 in ssubs:
                if ssub1 in v and ssub2 in v[ssub1]:
                    fw.write(";".join(v[ssub1][ssub2]) + "\t")
                else:
                    fw.write("\t")
            fw.write("\n")

    with open('database_generation/%s/output/subs_connect_table.txt' % database, 'w') as fw:
        ssubs = list(v.keys())
        s = set()
        for ssub1 in ssubs:
            for ssub2 in ssubs:
                k = ssub1+ssub2
                if k in s:
                    continue
                s.add(k)
                k2 = ssub2+ssub1
                if k2 in s:
                    continue
                s.add(k2)
                if ssub1 != ssub2 and ssub1 in v and ssub2 in v[ssub1]:
                    fw.write("%s\t%s\t%s\t%s\n" % (ssub1, ssub2, len(v[ssub1][ssub2]), ";".join(v[ssub1][ssub2])))


def write_meta_freq_files(database, v):
    with open('database_generation/%s/output/meta_compartment_freq.txt' % database, 'w') as fw:
        compts = [ci for ci in Compartment.objects.using(database).all().values_list('name', flat=True)]
        fw.write("#meta id\t" + "\t".join(compts) + "\n")
        for meta in v:
            fw.write(meta + "\t")
            for compt in compts:
                if compt in v[meta]['compartment']:
                    as_reactant = v[meta]['compartment'][compt]['reactant']
                    as_product = v[meta]['compartment'][compt]['product']
                    in_reaction = len(v[meta]['compartment'][compt]) - 2
                    fw.write("%s;%s;%s\t" % (in_reaction, as_reactant, as_product))
                else:
                    fw.write("\t")
            fw.write("\n")

    with open('database_generation/%s/output/meta_subsystem_freq.txt' % database, 'w') as fw:
        ssubs = [ss for ss in Subsystem.objects.using(database).all().values_list('name', flat=True)]
        fw.write("#meta id\t" + "\t".join(ssubs) + "\n")
        for meta in v:
            fw.write(meta + "\t")
            for ssub in ssubs:
                if ssub in v[meta]['subsystem']:
                    as_reactant = v[meta]['subsystem'][ssub]['reactant']
                    as_product = v[meta]['subsystem'][ssub]['product']
                    in_reaction = len(v[meta]['subsystem'][ssub]) - 2
                    fw.write("%s;%s;%s\t" % (in_reaction, as_reactant, as_product))
                else:
                    fw.write("\t")
            fw.write("\n")


def get_compt_subsystem_connectivity(database, compt_rme, rme_compt, sub_rme, rme_sub, compt_sub, compt_sub_reaction, pathway_compt_coverage):

        # metabolites that should be represented multiple time in the network, e.g H20
    high_freq_meta = {'M_m01597', 'M_m02348', 'M_m01371', 'M_m02877', 'M_m02759', 'M_m02552', 'M_m02046', 'M_m02039', \
     'M_m02900', 'M_m02555', 'M_m01980', 'M_m01802', 'M_m02914', 'M_m02554', 'M_m02026', 'M_m02519', 'M_m02553', \
      'M_m02040', 'M_m02901', 'M_m02630', 'M_m03107', 'M_m01334', 'M_m01450'}

    # read multi meta from svg file
    mm_svg = {}
    for ci in CompartmentSvg.objects.using(database).all():
        if ci.display_name[:7] == "Cytosol":
            continue
        mmeta_compartment = read_compartment_multi_metabolite(ci.filename)
        mm_svg[ci.display_name] = mmeta_compartment
        print ("%s : %s" % (ci.display_name, len(mmeta_compartment)))


    # define multiple metabolite
    global_compt_mm = set()
    global_ssub_mm = set()
    # metabolites to draw multiple time at compartment or subsystem level
    mm = {'compartment': {}, 'subsystem': {}}
    mm_compt_sub = {}
    subsystem_connection = {}
    unique_meta_ssub = {}

    result = {}

    for meta in rme_compt:
        # for each meta 
        # count when the meta is reactant or product in each reaction
        # store the infor for each compartment and for each subsystem where the reaction is
        if meta[0] != 'M':
            continue
        result[meta] = {'compartment': {}, 'subsystem': {}}
        reactions_as_reactant = {e for e in ReactionReactant.objects.using(database).filter(reactant_id=meta).values_list('reaction_id', flat=True)}
        for r_reaction in reactions_as_reactant:
            for cpmt in rme_compt[r_reaction]:
                if cpmt not in result[meta]['compartment']:
                    result[meta]['compartment'][cpmt] = {'reactant': 0, 'product': 0}
                if r_reaction not in result[meta]['compartment'][cpmt]:
                    result[meta]['compartment'][cpmt][r_reaction] = {'reactant': True, 'product': False}
                result[meta]['compartment'][cpmt]['reactant'] += 1

            for ssub in rme_sub[r_reaction]:
                if ssub not in result[meta]['subsystem']:
                    result[meta]['subsystem'][ssub] = {'reactant': 0, 'product': 0}
                if r_reaction not in result[meta]['subsystem'][ssub]:
                    result[meta]['subsystem'][ssub][r_reaction] = {'reactant': True, 'product': False}
                result[meta]['subsystem'][ssub]['reactant'] += 1
                if ssub[:10] == "Transport,":
                    pass
                    # do not count any transport reaction, is the reaction in transport ssub
                    '''for cpmt in rme_compt[r_reaction]:
                        if ssub in compt_sub[cpmt]:
                            result[meta]['compartment'][cpmt]['reactant'] -= 1'''

        reaction_as_product = {e for e in ReactionProduct.objects.using(database).filter(product_id=meta).values_list('reaction_id', flat=True)}
        for p_reaction in reaction_as_product:
            for cpmt in rme_compt[p_reaction]:
                if cpmt not in result[meta]['compartment']:
                    result[meta]['compartment'][cpmt] = {'reactant': 0, 'product': 0}
                if p_reaction not in result[meta]['compartment'][cpmt]:
                    result[meta]['compartment'][cpmt][p_reaction] = {'reactant': False, 'product': True}
                else:
                    result[meta]['compartment'][cpmt][p_reaction]['product'] = True
                result[meta]['compartment'][cpmt]['product'] += 1

            for ssub in rme_sub[p_reaction]:
                if ssub not in result[meta]['subsystem']:
                    result[meta]['subsystem'][ssub] = {'reactant': 0, 'product': 0}
                if p_reaction not in result[meta]['subsystem'][ssub]:
                    result[meta]['subsystem'][ssub][p_reaction] = {'reactant': False, 'product': True}
                else:
                    result[meta]['subsystem'][ssub][p_reaction]['product'] = True
                result[meta]['subsystem'][ssub]['product'] += 1
                if ssub[:10] == "Transport,":
                    pass
                    # do not count any transport reaction, is the reaction in transport ssub
                    '''for cpmt in rme_compt[p_reaction]:
                        if ssub in compt_sub[cpmt]:
                            result[meta]['compartment'][cpmt]['product'] -= 1'''

        reactions_as_reactant.union(reaction_as_product)
        if len(reactions_as_reactant) == 1:
            # meta in a single reaction, the meta is should me uniquely drawn
            continue

        # check if the meta should be drawn multiple time at the compartment lvl and subsystem of the compartment
        meta_ss_added = False
        for cpmt in result[meta]['compartment']:
            meta_compt_ss_added = False
            high_reaction_freq = set()
            # exclude Extracellular and Boundary, never drawn
            if cpmt in ['Extracellular', 'Boundary']:
                continue
            if len(result[meta]['compartment'][cpmt]) > 3: # 'reactant', 'product' and [reactions ids... > 1]
                # part of multiple reactions
                if (result[meta]['compartment'][cpmt]['reactant'] == 0 and result[meta]['compartment'][cpmt]['product'] != 1) or \
                   (result[meta]['compartment'][cpmt]['product'] == 0 and result[meta]['compartment'][cpmt]['reactant'] != 1) or \
                   result[meta]['compartment'][cpmt]['reactant'] > 1 or result[meta]['compartment'][cpmt]['product'] > 1:
                    if cpmt not in mm['compartment']:
                        mm['compartment'][cpmt] = set()
                    mm['compartment'][cpmt].add(meta)
                    meta_compt_ss_added = True
                    meta_ss_added = True
                    if len(result[meta]['compartment']) == 1:
                        global_compt_mm.add(meta)

                    if cpmt not in ['Cytosol', 'Peroxisome'] and meta not in mm_svg[cpmt]:
                        print ("warning: multi meta %s is not multi in svg, compartment %s" % (meta, cpmt))
                        #print (result[meta]['compartment'][cpmt])
                        #input()
                        # exit()

                if len(result[meta]['compartment'][cpmt]) > 12:
                    # more than 10 diff reactions
                    high_reaction_freq.add(meta)


                # check if unique in each subsystem, if true, the meta can be drawn uniquely and will connect
                # subsystem together
                single_in_one_subsystem = {}
                tot_as_reactant = 0
                tot_as_product = 0
                for ssub in compt_sub[cpmt]:
                    as_reactant = 0
                    as_product = 0
                    if ssub in result[meta]['subsystem']:
                        if ssub[:10] == "Transport,":
                            continue
                        for reaction in result[meta]['compartment'][cpmt]:
                            if reaction[0] != 'R':
                                # exclude {'reactant': 0, 'product': 0}
                                continue
                            if reaction in result[meta]['subsystem'][ssub]:
                                # consider only reactions of the ssub that are in the current compartment
                                if result[meta]['subsystem'][ssub][reaction]['reactant']:
                                    as_reactant += 1
                                    tot_as_reactant += 1
                                if result[meta]['subsystem'][ssub][reaction]['product']:
                                    as_product += 1
                                    tot_as_product += 1
                    if (as_reactant ==1 and as_product == 1) or \
                        (as_reactant == 1 and not as_product) or \
                        (as_product == 1 and not as_reactant) or \
                        (as_reactant and as_product and as_reactant + as_product <= 3):
                        single_in_one_subsystem[ssub] = True
                    elif as_reactant or as_product:
                        if cpmt not in mm_compt_sub:
                            mm_compt_sub[cpmt] = {}
                        if ssub not in mm_compt_sub[cpmt]:
                            mm_compt_sub[cpmt][ssub] = set()
                        mm_compt_sub[cpmt][ssub].add(meta)


                is_only_transport = False
                if tot_as_reactant == 0 and tot_as_product == 0:
                    is_only_transport = True

                if single_in_one_subsystem and meta not in high_reaction_freq:
                    keys = list(single_in_one_subsystem.keys())
                    for i in range(len(keys)):
                        for j in range(len(keys)):
                            if i == j:
                                continue
                            if keys[i] not in subsystem_connection:
                                subsystem_connection[keys[i]] = {}
                            if keys[j] not in subsystem_connection[keys[i]]:
                                subsystem_connection[keys[i]][keys[j]] = set()
                            subsystem_connection[keys[i]][keys[j]].add(meta)

                            if keys[j] not in subsystem_connection:
                                subsystem_connection[keys[j]] = {}
                            if keys[i] not in subsystem_connection[keys[j]]:
                                subsystem_connection[keys[j]][keys[i]] = set()
                            subsystem_connection[keys[j]][keys[i]].add(meta)

                    '''if is_multiple_in_one_subsystem:
                        if cpmt not in mm['compartment']:
                            mm['compartment'][cpmt] = set()
                        mm['compartment'][cpmt].add(meta)
                        meta_compt_ss_added = True
                        meta_ss_added = True
                        if len(result[meta]['compartment']) == 1:
                            global_compt_mm.add(meta)

                        if cpmt not in ['Cytosol', 'Peroxisome'] and meta not in mm_svg[cpmt]:
                            print ("second check")
                            print ("as_reactant: %s, as_product: %s (%s)" % (as_reactant, as_product, ssub))
                            print ("Error: multi meta %s is not multi in svg" % meta)
                            print ("compartment", cpmt)
                            print (result[meta]['compartment'][cpmt])
                            input()
                            # exit()'''

            # check if multi in svg but not found multi by the algo
            if cpmt not in ['Cytosol'] and not meta_compt_ss_added and meta in mm_svg[cpmt] and not is_only_transport:
                print ("warning: not multi meta %s is multi in svg, compartment %s" % (meta, cpmt))
                # print (result[meta]['compartment'][cpmt])
                # input()
                # exit()

        # check if the meta should be drawn multiple time at the subsystem lvl
        # without considering the compartment lvl

        for ssub in result[meta]['subsystem']:
            # filter Transport subsystem
            if ssub[:10] == "Transport,":
                continue
            if len(result[meta]['subsystem'][ssub]) > 3: # 'reactant', 'product' and [reactions ids... > 1]
                # part of multiple reactions
                if (result[meta]['subsystem'][ssub]['reactant'] == 0 and result[meta]['subsystem'][ssub]['product'] != 1) or \
                    (result[meta]['subsystem'][ssub]['product'] == 0 and result[meta]['subsystem'][ssub]['reactant'] != 1) or \
                    ((result[meta]['subsystem'][ssub]['reactant'] > 1 or result[meta]['subsystem'][ssub]['product'] > 1) and \
                    (result[meta]['subsystem'][ssub]['reactant'] + result[meta]['subsystem'][ssub]['product']) > 3):
                    # if only multiple times reactant or only multiple times product or several time both
                    if ssub not in mm['subsystem']:
                        mm['subsystem'][ssub] = set()
                    mm['subsystem'][ssub].add(meta)

                else:
                    if ssub not in unique_meta_ssub:
                        unique_meta_ssub[ssub] = set()
                    unique_meta_ssub[ssub].add(meta)

        # FIX ME? not M_m02012l is not multiple but get 2-2 reactant product in total 3 subsystems

    write_ssub_connection_files(database, subsystem_connection)

    write_meta_freq_files(database, result)

    with open("database_generation/%s/output/umeta_subsystem.txt" % database, 'w') as fw:
        for subsystem in unique_meta_ssub:
            fw.write("%s\t%s\n" % (subsystem, "; ".join(unique_meta_ssub[subsystem])))


def get_subsystem_compt_element(database):
    # get compartment statistics and check thaht every reaction/component
    # is assigned to subsystem and compartment
    compt_rme = {}
    rme_compt = {}
    compt_sub = {}
    compartments = Compartment.objects.using(database).all()
    for c in compartments:
        compt_metabolite_set = {e for e in ReactionComponent.objects.using(database).filter(compartment=c, component_type='m').values_list('id', flat=True)}
        compt_reaction = ReactionCompartment.objects.using(database).filter(compartment=c).values_list('reaction_id', flat=True)
        compt_reaction_set = {e for e in compt_reaction}
        compt_enzyme_set = {e for e in ReactionModifier.objects.using(database).filter(reaction_id__in=compt_reaction).values_list('modifier_id', flat=True)}
        
        print (c.name, "metabolite", len(compt_metabolite_set))
        print (c.name, "reaction", len(compt_reaction_set))
        print (c.name, "enzyme", len(compt_enzyme_set))

        # for each compartment stores the list of unique reactions/metabolite/enzyme
        compt_rme[c.name] = {
            'reaction': compt_reaction_set,
            'metabolite': compt_metabolite_set,
            'enzyme': compt_enzyme_set,
        }

        # for each reactions/metabolite/enzyme stores the list of compartments
        for r in compt_reaction_set:
            if r not in rme_compt:
                rme_compt[r] = set()
            rme_compt[r].add(c.name)
        for m in compt_metabolite_set:
            if m not in rme_compt:
                rme_compt[m] = set()
            rme_compt[m].add(c.name)
        for e in compt_enzyme_set:
            if e not in rme_compt:
                rme_compt[e] = set()
            rme_compt[e].add(c.name)

        compt_sub[c.name] = set()

    # get subsystem statistics
    subsystems = Subsystem.objects.using(database).all()
    sub_rme = {}
    rme_sub = {}
    for s in subsystems:
        sub_reaction_set = {e for e in SubsystemReaction.objects.using(database).filter(subsystem=s).values_list('reaction_id', flat=True)}
        sub_metabolite_set = {e for e in SubsystemMetabolite.objects.using(database).filter(subsystem=s).values_list('rc_id', flat=True)}
        sub_enzyme_set = {e for e in SubsystemEnzyme.objects.using(database).filter(subsystem=s).values_list('rc_id', flat=True)}

        # for each subsystem stores the list of unique reactions/metabolite/enzyme
        sub_rme[s.name] = {
            'reaction': sub_reaction_set,
            'metabolite': sub_metabolite_set,
            'enzyme': sub_enzyme_set,
        }

        for r in sub_reaction_set:
            if r not in rme_sub:
                rme_sub[r] = set()
            rme_sub[r].add(s.name)
            if r in rme_compt:
                # store the association compartment / subsystem
                for compt in rme_compt[r]:
                    compt_sub[compt].add(s.name)

        for m in sub_metabolite_set:
            if m not in rme_sub:
                rme_sub[m] = set()
            rme_sub[m].add(s.name)

        for e in sub_enzyme_set:
            if e not in rme_sub:
                rme_sub[e] = set()
            rme_sub[e].add(s.name)

    sub_compt_using_reaction = {}
    sub_compt_using_metabolite = {}
    sub_compt_using_enzyme = {}

    # get the association subsystem / compartment using the 3 components and compare
    for s_name in sub_rme:
        sub_compt_using_reaction[s_name] = set()
        sub_compt_using_metabolite[s_name] = set()
        sub_compt_using_enzyme[s_name] = set()

        for r in sub_rme[s_name]['reaction']:
            if r in rme_compt:
                for compt in rme_compt[r]:
                    sub_compt_using_reaction[s_name].add(compt)

        for m in sub_rme[s_name]['metabolite']:
            if m in rme_compt:
                for compt in rme_compt[m]:
                    sub_compt_using_metabolite[s_name].add(compt)

        for e in sub_rme[s_name]['enzyme']:
            if e in rme_compt:
                for compt in rme_compt[e]:
                    sub_compt_using_enzyme[s_name].add(compt)


        print (s_name, len(sub_compt_using_reaction[s_name]), len(sub_compt_using_metabolite[s_name]), len(sub_compt_using_enzyme[s_name]))
        if len(sub_compt_using_reaction[s_name]) != len(sub_compt_using_metabolite[s_name]):
            # ignore relation get with enzymes cause it give more compartments
            # enzyme ids are not duplicated like metabolite
            print ("Error")
            print (sub_compt_using_reaction[s_name], sub_compt_using_metabolite[s_name])
            exit(1)

        print ("sub_compt_using_reaction", sub_compt_using_reaction[s_name])
        print ("sub_compt_using_metabolite", sub_compt_using_metabolite[s_name])
        print ("sub_compt_using_enzyme", sub_compt_using_enzyme[s_name])
        print ("###################################")

    reaction_not_compt = []
    reaction_not_sub = []
    metabolite_not_compt = []
    metabolite_not_sub = []
    enzyme_not_compt = []
    enzyme_not_sub = []

    # check if there is reaction not assigned to any compartment/subsystem
    for r in Reaction.objects.using(database).all():
        if r.id not in rme_compt:
            reaction_not_compt.append(r.id)
        if r.id not in rme_sub:
            reaction_not_sub.append(r.id)

    # check if there is enzyme/metabolite not assigned to any compartment/subsystem
    for rc in ReactionComponent.objects.using(database).all():
        if rc.component_type == 'e':
            if rc.id not in rme_compt:
                enzyme_not_compt.append(rc.id)
            if rc.id not in rme_sub:
                enzyme_not_sub.append(rc.id)
        elif rc.component_type == 'm':
            if rc.id not in rme_compt:
                metabolite_not_compt.append(rc.id)
            if rc.id not in rme_sub:
                metabolite_not_sub.append(rc.id)
        else:
            print ("Error: component type = '%s'" % rc.component_type)
            exit(1)

    print ("not r in c: ", len(reaction_not_compt), len(set(reaction_not_compt)))
    print ("not r in s: ", len(reaction_not_sub), len(set(reaction_not_sub)))
    print ("not m in c: ", len(metabolite_not_compt), len(set(metabolite_not_compt)))
    print ("not m in s: ", len(metabolite_not_sub), len(set(metabolite_not_sub)))
    print ("not e in c: ", len(enzyme_not_compt), len(set(enzyme_not_compt)))
    print ("not e in s: ", len(enzyme_not_sub), len(set(enzyme_not_sub)))

    if len(reaction_not_compt) or \
        len(reaction_not_sub) or \
        len(metabolite_not_compt) or \
        len(metabolite_not_sub) or \
        len(enzyme_not_compt) or \
        len(enzyme_not_sub):
        print ("Error")
        exit(1)

    # get subsystem compartment coverage
    compt_sub_reaction = {}
    pathway_compt_coverage = {}
    for c in compartments:
        compt_reaction = compt_rme[c.name]['reaction']
        for s in subsystems:
            sub_reaction = sub_rme[s.name]['reaction']

            # store stats
            if s.name not in pathway_compt_coverage:
                pathway_compt_coverage[s.name] = [len(sub_reaction), {}]

            r_overlap = {r for r in sub_reaction if r in compt_reaction}
            if c.name not in compt_sub_reaction:
                compt_sub_reaction[c.name] = {}
            if s.name not in compt_sub_reaction[c.name]:
                compt_sub_reaction[c.name][s.name] = set()
            # store list of reactions per compt-subsystem
            compt_sub_reaction[c.name][s.name].update(r_overlap)

            if len(r_overlap) != 0:
                print ("Cmp %s - Reactions found in '%s': %s | overlap: %s (%s)" % \
                    (c.name, s.name, len(sub_reaction), len(r_overlap), float(len(r_overlap))/len(sub_reaction) * 100.0))
                pathway_compt_coverage[s.name][1][c.name] = len(r_overlap) # store the overlap with the current compartment
    '''
    pathway_compt_coverage:

    {'Transport, nuclear': 
        [75, # total reaction
        {'Extracellular': 0,
         'Peroxisome': 0,
         'Endoplasmic reticulum': 1,
         'Lysosome': 0,
         'Mitochondria': 0,
         'Boundary': 0,
         'Golgi apparatus': 0,
         'Nucleus': 74,
         'Cytosol': 74
         }
         ],
     'Beta oxidation of unsaturated fatty acids (n-9)':
         [59, {  ... }],
     'Purine metabolism': ...

    '''

    return compt_rme, rme_compt, sub_rme, rme_sub, compt_sub, sub_compt_using_reaction, compt_sub_reaction, pathway_compt_coverage


def get_subsystem_compt_element_svg(database):
    # store compartment / subsystem relationship in the svg file
    # and compartment / enzyme-metabolite-reaction
    # note: there is no information about subsystem / enzyme-metabolite-reaction that
    # can be extracted from the svg
    compt_rme_svg = {}
    rme_compt_svg = {}
    compt_sub_svg = {}
    sub_compt_svg = {}

    for ci in CompartmentSvg.objects.using(database).all():
        reaction_compartment = read_compartment_reaction(ci.filename)
        metabolite_compartment = read_compartment_metabolite(ci.filename)
        enzyme_compartment = read_compartment_enzyme(ci.filename)
        subsystem_compartment = read_compartment_subsystem(database, ci.filename)

        print ("Reactions found in the SVG file '%s': %s" % (ci.display_name, len(reaction_compartment)))
        print ("Metabolites found in the SVG file '%s': %s" % (ci.display_name, len(metabolite_compartment)))
        print ("Enzymes found in the SVG file '%s': %s" % (ci.display_name, len(enzyme_compartment)))
        print ("Subsystem found in the SVG file '%s': %s" % (ci.display_name, len(subsystem_compartment)))

        compt_rme_svg[ci.display_name] = {
            'reaction': {e for e in reaction_compartment},
            'metabolite': {e for e in metabolite_compartment},
            'enzyme': {e for e in enzyme_compartment}
        }

        for r in reaction_compartment:
            if r not in rme_compt_svg:
                rme_compt_svg[r] = set()
            rme_compt_svg[r].add(ci.display_name)
        for m in metabolite_compartment:
            if m not in rme_compt_svg:
                rme_compt_svg[m] = set()
            rme_compt_svg[m].add(ci.display_name)
        for e in enzyme_compartment:
            if e not in rme_compt_svg:
                rme_compt_svg[e] = set()
            rme_compt_svg[e].add(ci.display_name)

        for s in subsystem_compartment:
            if ci.display_name not in compt_sub_svg:
                compt_sub_svg[ci.display_name] = set()
            compt_sub_svg[ci.display_name].add(s)

            if s not in sub_compt_svg:
                sub_compt_svg[s] = set()
            sub_compt_svg[s].add(ci.display_name)

        # create the key even if there is no subsystem (case of Cytosol 6)
        if ci.display_name not in compt_sub_svg:
            compt_sub_svg[ci.display_name] = set()

    return compt_rme_svg, rme_compt_svg, compt_sub_svg, sub_compt_svg


def saveSubsystemCompartment(database, sub_compt_using_reaction):
    # save the connection subsystem / compartement base on the reaction
    # reaction are part of subsystem and involve metabolites located in one or more compartments
    for subsystem, compartments in sub_compt_using_reaction.items():
        ss = Subsystem.objects.using(database).get(name=subsystem)
        for compartment in compartments:
            compt = Compartment.objects.using(database).get(name=compartment)

            try:
                sc = SubsystemCompartment.objects.using(database).get(subsystem=ss, compartment=compt)
            except SubsystemCompartment.DoesNotExist:
                sc = SubsystemCompartment(subsystem=ss, compartment=compt)
                sc.save(using=database)


def saveTileSubsystem(database, compt_sub_svg, compt_sub, compt_rme_svg, compt_rme, sub_rme, compt_sub_reaction):
    for c_name_svg in compt_rme_svg: # all compartments having a svg file (cytosol splited)
        ci = CompartmentSvg.objects.using(database).get(display_name=c_name_svg)
        reaction_svg = compt_rme_svg[c_name_svg]['reaction']

        if c_name_svg.startswith("Cytosol"):
            c_name = 'Cytosol'
        else:
            c_name = c_name_svg
        if c_name not in compt_sub:
            # check if the cpt name exist in the database
            print ("Error: compartment %s not in db" % c_name)
            exit(1)

        subsystem_svg = compt_sub_svg[c_name_svg]
        for s_name in subsystem_svg: # all subsystem that exists in the current compartments / svg file
            s = Subsystem.objects.using(database).get(name=s_name)
            if s.system == 'Collection of reactions':
                # ignore collection of reactions pathways
                # pathways = Subsystem.objects.using(database).exclude(system='Collection of reactions')
                continue

            # check if the subsystem is in the compartment:
            if s_name not in compt_sub[c_name]:
                print ("Error: subsystem '%s' not in compartment '%s' in DB" % (s_name, c_name))
                exit(1)

            # get all reaction in the current subsystem
            # this information is taken from the database not from the svg
            # currently there is no way to get this info from the svg
            reaction_db = sub_rme[s_name]['reaction'] # set of reaction id
            r_overlap = reaction_svg & reaction_db
            if not r_overlap:
                continue
                print ("Cannot get coord box for pathway %s" % s.name)
                exit(1)


            reaction_svg_cood = read_compartment_reaction(ci.filename)
            reaction_svg_cood = [reaction_svg_cood[e] for e in reaction_svg_cood if e in r_overlap]
            pw_svg_name = is_compartment_pathway(ci.filename, s.name)
            if not pw_svg_name and ci.display_name != "Cytosol_6":
                # ignore Cytosol 6, the map is unfinished
                print ("pw %s not in compartment %s: %s" % (s.name, ci.display_name, is_pw_in_compartment))
                print ("but %s reactions are" % len(r_overlap))
                exit(1)

            # create tileSubtitle only if got coordinates
            # TODO get coor of the subsystem using pw_svg_name
            box = getMinAndMax(reaction_svg_cood)
            if not box:
                print ("Error: cannot get coordinate for pathway: %s in compartment %s" % (s.name, ci.display_name))
                exit(1)

            # check if exists
            ss = Subsystem.objects.using(database).get(id=s.id)
            # TODO check if the pathway is really visible in the svg
            try:
                t = TileSubsystem.objects.using(database).get(subsystem=ss, compartment_name=ci.display_name)
                '''print ("Already exists")
                print (t.x_top_left, t.y_top_left, int(box[0]-padding), int(box[1]-padding))
                assert t.x_top_left == int(box[0]-padding)
                assert t.y_top_left == int(box[1]-padding)'''
            except TileSubsystem.DoesNotExist:
                # link subsysbtem / compartment base on the reactions drawn in the svg, metabolite / enzymes can be missing
                # there might be missing reactions or additional ones per compartment maps
                t = TileSubsystem(subsystem=ss, subsystem_name=s.name,
                    compartmentsvg=ci,
                    compartment_name=ci.display_name,
                    x_top_left=box[0], y_top_left=box[1],
                    x_bottom_right=box[2], y_bottom_right=box[3],
                    reaction_count=len(r_overlap)) # store the real number of reaction in the compartment
                t.save(using=database)


def processData(database, compartment_svg_file=False, write_connectivity_files=False):
    """ Read the Compartment Information base data from file """
    # insert svg compartment
    if compartment_svg_file:
        with open(compartment_svg_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for ci in reader:
                c = Compartment.objects.using(database).filter(name=ci[0])
                if not c:
                    print("Cant match the compartment information name "+ci[0]+" to a compartment...")
                    exit(1)

                try:
                    cinfo = CompartmentSvg.objects.using(database).get(display_name=ci[1])
                except CompartmentSvg.DoesNotExist:
                    cinfo = CompartmentSvg(display_name=ci[1], filename=ci[2], compartment=c[0], letter_code=ci[3])
                    cinfo.save(using=database)

    # get element in subsystem / compt from database
    compt_rme, rme_compt, sub_rme, rme_sub, compt_sub, sub_compt_using_reaction, \
     compt_sub_reaction, pathway_compt_coverage = get_subsystem_compt_element(database)

    get_compt_subsystem_connectivity(database, compt_rme, rme_compt, sub_rme, rme_sub, compt_sub, compt_sub_reaction, pathway_compt_coverage)

    # get element in subsystem / compt from svg
    compt_rme_svg, rme_compt_svg, compt_sub_svg, sub_compt_svg = get_subsystem_compt_element_svg(database)

    # compare M, R, E localization between SVG and database
    for compt in compt_rme_svg:
        print ("====", compt)
        d_svg = compt_rme_svg[compt]
        if compt.startswith("Cytosol"):
            cyto = True
            compt_db = "Cytosol"
        else:
            cyto = False
            compt_db = compt
        if compt_db in compt_rme:
            d = compt_rme[compt_db]
            union_reaction = d_svg['reaction'] & d['reaction']
            print ("reaction: ", len(d_svg['reaction']), len(d['reaction']), len(union_reaction))
            if len(union_reaction) != len(d_svg['reaction']) or len(union_reaction) != len(d['reaction']):
                not_in_svg = d['reaction'] - d_svg['reaction']
                not_in_db = d_svg['reaction'] - d['reaction']
                print("Not in svg: %s | not in db %s" % (len(not_in_svg), len(not_in_db)))
                if not_in_svg and not cyto:
                    print ("Not in svg:", not_in_svg)
                if not_in_db:
                    print ("Not in db:", not_in_db)

            union_metabolite = d_svg['metabolite'] & d['metabolite']
            print ("metabolite: ", len(d_svg['metabolite']), len(d['metabolite']), len(d_svg['metabolite'] & d['metabolite']))
            if len(union_metabolite) != len(d_svg['metabolite']) or len(union_metabolite) != len(d['metabolite']):
                not_in_svg = d['metabolite'] - d_svg['metabolite']
                not_in_db = d_svg['metabolite'] - d['metabolite']
                print("Not in svg: %s | not in db %s" % (len(not_in_svg), len(not_in_db)))
                if not_in_svg and not cyto:
                    print ("Not in svg:", not_in_svg)
                if not_in_db:
                    print ("Not in db:", not_in_db)

            union_enzyme = d_svg['enzyme'] & d['enzyme']
            print ("enzyme: ", len(d_svg['enzyme']), len(d['enzyme']), len(d_svg['enzyme'] & d['enzyme']))
            if len(union_enzyme) != len(d_svg['enzyme']) or len(union_enzyme) != len(d['enzyme']):
                not_in_svg = d['enzyme'] - d_svg['enzyme']
                not_in_db = d_svg['enzyme'] - d['enzyme']
                print("Not in svg: %s | not in db %s" % (len(not_in_svg), len(not_in_db)))
                if not_in_svg and not cyto:
                    print ("Not in svg:", not_in_svg)
                if not_in_db:
                    print ("Not in db:", not_in_db)

        else:
            print ("Error: unknown compartment %s" % compt)
            print ("reaction: ", len(d_svg['reaction']))
            print ("metabolite: ", len(d_svg['metabolite']))
            print ("enzyme: ", len(d_svg['enzyme']))
            exit(1)

    # compare subsystem
    s_svg_cyto_tot = set()
    for compt in compt_rme_svg:
        print ("====", compt)
        d_svg = compt_rme_svg[compt]
        if compt.startswith("Cytosol"):
            cyto = True
            compt_db = "Cytosol"
        else:
            cyto = False
            compt_db = compt
        if compt not in compt_sub_svg:
            print ("Compartment svg %s not not have any subsystem" % compt)
            s_svg = False
        else:
            s_svg = compt_sub_svg[compt]
            # check overlap with the whole cytosol compartment
            if cyto:
                s_svg_cyto_tot.update(compt_sub_svg[compt])
            print ("subsystem svg: %s "% len(s_svg))
        if compt_db not in compt_sub:
            print ("Compartment %s not not have any subsystem" % compt_db)
            s_db = False
        else:
            s_db = compt_sub[compt_db]
            print ("subsystem: %s "% len(s_db))
        if s_svg and s_db:
            ovlp = s_svg & s_db
            not_in_svg = s_db - s_svg
            mot_in_db = s_svg - s_db
            print ("overlap: %s (not in svg %s) (not in db %s)" % (len(ovlp), len(not_in_svg), len(not_in_db)))
            if not_in_svg and not cyto:
                print ("Not in svg:", not_in_svg)
            if not_in_db:
                print ("Not in db:", not_in_db)

    print
    print ("%s total subsystem have been found in svg / %s in database" % (len(s_svg_cyto_tot), len(compt_sub['Cytosol'])))
    print ("overlaping subsystems: %s" % len((s_svg_cyto_tot & compt_sub['Cytosol'])))
    input("continue?")

    saveSubsystemCompartment(database, sub_compt_using_reaction)

    saveTileSubsystem(database, compt_sub_svg, compt_sub, compt_rme_svg, compt_rme, sub_rme, compt_sub_reaction)

    if write_connectivity_files:
        write_subsystem_summary_file(database, rme_compt_svg, sub_compt_svg, pathway_compt_coverage)

    subsystems = Subsystem.objects.using(database).exclude(system='Collection of reactions')
    subsystem_stat_dict = {}
    compart_stat_dict = {}

    setAsMainIfInOnlyOneCompartment(database)
    # manuallySetSomeAsMain(database)
    autoSetIsMain(database, pathway_compt_coverage)

    # update subsystem stats
    for s in subsystems:
        subsystem = Subsystem.objects.using(database).get(name=s.name)

        # from SBML
        smsQuerySet = SubsystemMetabolite.objects.using(database). \
            filter(subsystem_id=subsystem).values_list('rc_id', flat=True)
        unique_meta = set()
        for meta_id in smsQuerySet:
            unique_meta.add(meta_id[:-1])
        sesQuerySet = SubsystemEnzyme.objects.using(database). \
            filter(subsystem_id=subsystem).values_list('rc_id', flat=True)
        srsQuerySet = SubsystemReaction.objects.using(database). \
            filter(subsystem_id=subsystem).values_list('reaction_id', flat=True)

        compartment_meta = ReactionComponent.objects.using(database). \
            filter(id__in=smsQuerySet).values_list('compartment', flat=True).distinct()
        compartment_meta = Compartment.objects.using(database).filter(id__in=compartment_meta).values_list('name', flat=True)

        compartment_enz = ReactionComponent.objects.using(database). \
            filter(id__in=sesQuerySet).values_list('compartment', flat=True).distinct()
        compartment_enz = Compartment.objects.using(database).filter(id__in=compartment_enz).values_list('name', flat=True)

        compartment_eq = Reaction.objects.using(database). \
             filter(id__in=srsQuerySet).values_list('compartment', flat=True).distinct()
        compartment_react = []
        for el in compartment_eq:
            compartment_react += [c.strip() for c in re.split('[+]|(?:=>)', el) if c]

        # check if compartment list for meta/enz/react are the same
        # ignore compartment_enz, they are all annotated to be in the cytosol
        if set(compartment_meta) != set(compartment_react):
            # should not be possible
            print ("error: compartment !=")
            print ("Metabolite: ", set(compartment_meta))
            print ("Enzyme: ", set(compartment_enz))
            print ("Reaction: ", set(compartment_react))
            exit(1)

        print ("Metabolites: ", smsQuerySet.count())
        print ("Enzymes: ", sesQuerySet.count())
        print ("Reactions: ", srsQuerySet.count())
        print ("Compartment: ", len(set(compartment_meta)))

        subsystem.reaction_count = srsQuerySet.count()
        subsystem.enzyme_count = sesQuerySet.count()
        subsystem.metabolite_count = smsQuerySet.count()
        subsystem.unique_metabolite_count = len(unique_meta)
        subsystem.compartment_count = len(set(compartment_meta))
        subsystem.save(using=database)


    # update subsystem svg stat
    for p_name, v in pathway_compt_coverage.items():
        # stats display on the HMR web site are the one that correspond to the model file
        # so skip it for now
        continue

    if compartment_svg_file:
        # compartment svg stats, values correspond to what is inside the svg files
        # whenever svg files changer, run again
        # python manage.py addCompartmentInformation database_generation/data/compartmentInfo.tab [database]
        cis = CompartmentSvg.objects.using(database).all()
        for ci in cis:
            rcs = ReactionComponent.objects.using(database).filter(id__in=compt_rme_svg[ci.display_name]['metabolite'])
            metabolite_count = 0
            for rc in rcs:
                rccis = ReactionComponentCompartmentSvg.objects.using(database). \
                    filter(rc=rc, compartmentsvg=ci)
                if not rccis:
                    add = ReactionComponentCompartmentSvg(rc=rc, compartmentsvg=ci)
                    add.save(using=database)
                metabolite_count += 1

            # add the connection to the reactions
            rs = Reaction.objects.using(database).filter(id__in=compt_rme_svg[ci.display_name]['reaction'])
            for r in rs:
                rcis = ReactionCompartmentSvg.objects.using(database). \
                    filter(reaction=r, compartmentsvg=ci)
                if not rcis:
                    add = ReactionCompartmentSvg(reaction=r, compartmentsvg=ci)
                    add.save(using=database)
            reaction_count = len(list(rs))

            rcs = ReactionComponent.objects.using(database).filter(id__in=compt_rme_svg[ci.display_name]['enzyme'])
            enzyme_count = 0
            for rc in rcs:
                rccis = ReactionComponentCompartmentSvg.objects.using(database). \
                    filter(rc=rc, compartmentsvg=ci)
                if not rccis:
                    add = ReactionComponentCompartmentSvg(rc=rc, compartmentsvg=ci)
                    add.save(using=database)
                enzyme_count += 1

            # how many subsystems?
            subsystem_count = len(compt_sub_svg[ci.display_name])

            # finally update the object
            # stats display on the HMR web site are the one that correspond to the model file
            # thus stats should not be use when query about cytosol_x
            CompartmentSvg.objects.using(database). \
                filter(id=ci.id).update(reaction_count=reaction_count, subsystem_count=subsystem_count, \
                 metabolite_count=metabolite_count, enzyme_count=enzyme_count)  # nr_unique_meta is not updated

    # get compartment statistics from the database
    cis = CompartmentSvg.objects.using(database).all()
    for ci in cis:
        sql = """SELECT * FROM reaction_component WHERE id in (
                    select reactant_id from reaction_reactant where reaction_id in (
                      select reaction_id from subsystem_reaction where subsystem_id in (
                        select subsystem_id from tile_subsystems where compartmentsvg_id=%s)))
        """ % ci.id
        rcs = ReactionComponent.objects.using(database).raw(sql)
        metabolite_count = len(list(rcs))

        # add the connection to the reactions
        sql = """SELECT * FROM reaction WHERE id in (
                    select reaction_id from subsystem_reaction where subsystem_id in (
                      select subsystem_id from tile_subsystems where compartmentsvg_id=%s))
        """ % ci.id
        rs = Reaction.objects.using(database).raw(sql)
        reaction_count = len(list(rs))

        # how many subsystems?
        sql = """SELECT * from subsystem WHERE id in ( \
                    select subsystem_id from tile_subsystems where compartmentsvg_id=%s)""" % ci.id
        s = Subsystem.objects.using(database).raw(sql)
        subsystem_count = len(list(s))

        # how many enzymes?
        sql = """SELECT * FROM reaction_component WHERE id in (
                   select modifier_id from reaction_modifier where reaction_id in (
                     select reaction_id from subsystem_reaction where subsystem_id in (
                       select subsystem_id from tile_subsystems where compartmentsvg_id=%s)))
        """ % ci.id
        rcs = ReactionComponent.objects.using(database).raw(sql)
        enzyme_count = len(list(rcs))

        # finally update the stats
        # stats display on the HMR web site are the one that correspond to the model file
        Compartment.objects.using(database). \
            filter(id=ci.compartment.id).update(reaction_count=reaction_count, subsystem_count=subsystem_count, \
             metabolite_count=metabolite_count, enzyme_count=enzyme_count)


class Command(BaseCommand):

    def add_arguments(self, parser):
        import argparse
        parser.add_argument('database', type=str)
        parser.add_argument('--compartment-svg-file', type=str, dest='compartment_svg_file')
        parser.add_argument('--write-connectivity-files', action="store_true", default=False, dest='write_connectivity')

    def handle(self, *args, **options):
        '''if options['include_svg']:
            print ("Make sure you put the last svg files version in backend/svgs")
            input()'''

        # 
        #
        #
        processData(options['database'], compartment_svg_file=options['compartment_svg_file'], write_connectivity_files=options['write_connectivity'])
