###########################################################
### Go through all pathways and figure out X,Y for them ###
###########################################################
import csv
import os
import re
import operator
import hashlib

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand
from django.db import connection
from django.db import connections
from django.db.models import Q


def file_as_bytes(file):
    with file:
        return file.read()


def read_map_reaction(filePath):
    """ Read svgs file and get all reactions ID and its coordinate x,y """
    res = set()
    with open(filePath, "r") as myfile:
        data = myfile.readlines()
        for idx, l in enumerate(data):
            l = l.strip()
            m = re.match('<g id="([^"]+)" class="rea"', l)
            if m:
                rid = m.group(1)
                res.add(rid)
    return res


def read_map_metabolite(filePath):
    res = set()
    with open(filePath, "r") as myfile:
        data = myfile.readlines()
        for idx, l in enumerate(data):
            l = l.strip()
            m = re.match('<g class="met ([^" ]+)', l)
            if m:
                rid = m.group(1)
                res.add(rid)
    return res


def read_map_enzyme(filePath):
    res = set()
    with open(filePath, "r") as myfile:
        data = myfile.readlines()
        for idx, l in enumerate(data):
            l = l.strip()
            m = re.match('<g class="enz ([^" ]+)', l)
            if m:
                rid = m.group(1)
                res.add(rid)
    return res


def read_map_subsystem(database, filePath):
    res = set()
    with open(filePath, "r") as myfile:
        data = myfile.readlines()
        for idx, l in enumerate(data):
            l = l.strip()
            m = re.match('<g id="([^"]+)" class="subsystem" ', l)
            if m:
                sid = m.group(1)
                # sid = get_real_subsystem_name(database, sid, filePath)
                res.add(sid)
    return res


def write_subsystem_summary_file(database, rme_compt_svg, sub_compt_svg, pathway_compt_coverage):
    # read the subsystem from db to get the system and keep the same order
    subsystems = Subsystem.objects.using(database).all()
    subsystems = sorted(subsystems, key=operator.attrgetter('name'))

    cor = []
    with open("database_generation/%s/output/subsystem.txt" % database, 'w') as fw:
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


def write_ssub_connection_files(database, v):
    try:
        os.makedirs('database_generation/%s/output/' % database)
    except:
        pass
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

    connection_count = []
    setk = set(v.keys())
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
                    connection_count.append(ssub1)
                    connection_count.append(ssub2)
                    fw.write("%s\t%s\t%s\t%s\n" % (ssub1, ssub2, len(v[ssub1][ssub2]), ";".join(v[ssub1][ssub2])))
    import collections
    with open('database_generation/%s/output/subs_connect_count.txt' % database, 'w') as fw:
        for sub, count in collections.Counter(connection_count).items():
             fw.write("%s\t%s\n" % (sub, count))


def write_meta_freq_files(database, v):
    try:
        os.makedirs('database_generation/%s/output/' % database)
    except:
        pass
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


def get_compt_subsystem_connectivity(database, map_directory, compt_rme, rme_compt, sub_rme, rme_sub, compt_sub, compt_sub_reaction, pathway_compt_coverage):

    # metabolites that should be represented multiple time in the network, e.g H20
    high_freq_meta = {'M_m01597', 'M_m02348', 'M_m01371', 'M_m02877', 'M_m02759', 'M_m02552', 'M_m02046', 'M_m02039', \
     'M_m02900', 'M_m02555', 'M_m01980', 'M_m01802', 'M_m02914', 'M_m02554', 'M_m02026', 'M_m02519', 'M_m02553', \
      'M_m02040', 'M_m02901', 'M_m02630', 'M_m03107', 'M_m01334', 'M_m01450'}

    # not used
    high_freq_meta = ReactionComponent.objects.using(database).filter(is_currency=True).values_list('id', flat=True)

    # read multi meta from svg file
    mm_svg = {}
    for ci in CompartmentSvg.objects.using(database).all():
        # if ci.name[:7] == "Cytosol":
        #     continue
        try:
            mmeta_compartment = read_map_multi_metabolite(os.path.join(map_directory, ci.filename))
            mm_svg[ci.name] = mmeta_compartment
            print ("%s : %s" % (ci.name, len(mmeta_compartment)))
        except Exception as e:
            print(e)


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
        # store the info for each compartment and for each subsystem where the reaction is
        if meta[:6] == 'ENSG00': # TODO change me, model specific to ensembl gene id
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
                if ssub[:10] == "Transport," or ssub == "Transport" or ssub == "Exchange/demand reactions":
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
                if ssub[:10] == "Transport," or ssub == "Transport" or ssub == "Exchange/demand reactions":
                    pass
                    # do not count any transport reaction, is the reaction in transport ssub
                    '''for cpmt in rme_compt[p_reaction]:
                        if ssub in compt_sub[cpmt]:
                            result[meta]['compartment'][cpmt]['product'] -= 1'''

        reactions_as_reactant.union(reaction_as_product)
        if len(reactions_as_reactant) == 1:
            # meta in a single reaction, the meta is should be uniquely drawn
            continue

        # check if the meta should be drawn multiple time at the compartment lvl and subsystem of the compartment
        meta_ss_added = False
        for cpmt in result[meta]['compartment']:
            meta_compt_ss_added = False
            high_reaction_freq = set()
            # exclude Extracellular and Boundary, not drawn
            if cpmt in ['Extracellular', 'Boundary']:
                continue
            if len(result[meta]['compartment'][cpmt]) > 3: # 'reactant', 'product' and [reactions ... > 1]
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

                    if mm_svg and cpmt not in ['Cytosol'] and meta not in mm_svg[cpmt]:
                        print ("warning: multi meta %s is not multi in svg, compartment %s" % (meta, cpmt))
                        #print (result[meta]['compartment'][cpmt])
                        #input()
                        # exit()

                if len(result[meta]['compartment'][cpmt]) > 12:
                    # in more than 10 diff reactions
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
                        if ssub[:10] == "Transport," or ssub == "Transport" or ssub == "Exchange/demand reactions":
                            continue
                        for reaction in result[meta]['compartment'][cpmt]:
                            if reaction == 'reactant' or reaction == 'product':
                                continue
                            if reaction in result[meta]['subsystem'][ssub]:
                                # consider only reactions of the ssub that are in the current compartment
                                if result[meta]['subsystem'][ssub][reaction]['reactant']:
                                    as_reactant += 1
                                    tot_as_reactant += 1
                                if result[meta]['subsystem'][ssub][reaction]['product']:
                                    as_product += 1
                                    tot_as_product += 1
                    if (as_reactant == 1 and as_product == 1) or \
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
            if cpmt in mm_svg not in ['Cytosol'] and not meta_compt_ss_added and meta in mm_svg[cpmt] and not is_only_transport:
                print ("warning: not multi meta %s is multi in svg, compartment %s" % (meta, cpmt))
                # print (result[meta]['compartment'][cpmt])
                # input()
                # exit()

        # check if the meta should be drawn multiple time at the subsystem lvl
        # without considering the compartment lvl
        for ssub in result[meta]['subsystem']:
            # filter Transport subsystem
            if ssub[:10] == "Transport," or ssub == "Transport" or ssub == "Exchange/demand reactions":
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

def get_components_interconnection(database):
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
            print ("Error: != number of compt associate to subsystem  %s, when using reaction or metabolite")
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
        print (enzyme_not_sub[:10])
        print ("Error")
        exit(1)

    # get subsystem compartment coverage
    compt_sub_reaction = {}
    pathway_compt_coverage = {}
    with open("database_generation/%s/output/compt_subsystem_coverage.txt" % database, 'w') as fw:
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
                    res_string = "Cmp %s - Reactions found in '%s': %s | overlap: %s (%s)" % \
                        (c.name, s.name, len(sub_reaction), len(r_overlap), float(len(r_overlap))/len(sub_reaction) * 100.0)
                    print (res_string)
                    fw.write("%s\t%s\t%s\t%s\t%s\n" % \
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

def get_subsystem_compt_element_svg_global(database, map_directory):
    # store compartment / subsystem relationship in the svg file
    # and compartment / enzyme-metabolite-reaction
    # note: there is no information about subsystem / enzyme-metabolite-reaction that
    # can be extracted from the svg
    compt_rme_svg = {}
    rme_compt_svg = {}
    compt_sub_svg = {}
    sub_compt_svg = {}

    for ci in CompartmentSvg.objects.using(database).all():
        reaction_compartment = read_map_reaction(os.path.join(map_directory, ci.filename))
        metabolite_compartment = read_map_metabolite(os.path.join(map_directory, ci.filename))
        enzyme_compartment = read_map_enzyme(os.path.join(map_directory, ci.filename))
        subsystem_compartment = read_map_subsystem(os.path.join(map_directory, database, ci.filename))

        print ("Reactions found in the SVG file '%s': %s" % (ci.name, len(reaction_compartment)))
        print ("Metabolites found in the SVG file '%s': %s" % (ci.name, len(metabolite_compartment)))
        print ("Enzymes found in the SVG file '%s': %s" % (ci.name, len(enzyme_compartment)))
        print ("Subsystem found in the SVG file '%s': %s" % (ci.name, len(subsystem_compartment)))

        compt_rme_svg[ci.name] = {
            'reaction': {e for e in reaction_compartment},
            'metabolite': {e for e in metabolite_compartment},
            'enzyme': {e for e in enzyme_compartment}
        }

        for r in reaction_compartment:
            if r not in rme_compt_svg:
                rme_compt_svg[r] = set()
            rme_compt_svg[r].add(ci.name)
        for m in metabolite_compartment:
            if m not in rme_compt_svg:
                rme_compt_svg[m] = set()
            rme_compt_svg[m].add(ci.name)
        for e in enzyme_compartment:
            if e not in rme_compt_svg:
                rme_compt_svg[e] = set()
            rme_compt_svg[e].add(ci.name)

        for s in subsystem_compartment:
            if ci.name not in compt_sub_svg:
                compt_sub_svg[ci.name] = set()
            compt_sub_svg[ci.name].add(s)

            if s not in sub_compt_svg:
                sub_compt_svg[s] = set()
            sub_compt_svg[s].add(ci.name)

        # create the key even if there is no subsystem (case of Cytosol 6)
        if ci.name not in compt_sub_svg:
            compt_sub_svg[ci.name] = set()

    return compt_rme_svg, rme_compt_svg, compt_sub_svg, sub_compt_svg


def parse_svg(database, component, map_directory):
    # store compartment / subsystem relationship in the svg file
    # and compartment / enzyme-metabolite-reaction
    # note: there is no information about subsystem / enzyme-metabolite-reaction that
    # can be extracted from the svg

    reaction_component = read_map_reaction(os.path.join(map_directory, component.filename))
    metabolite_component = read_map_metabolite(os.path.join(map_directory, component.filename))
    enzyme_component = read_map_enzyme(os.path.join(map_directory, component.filename))
    subsystem_component = read_map_subsystem(database, os.path.join(map_directory, component.filename))

    print ("Reactions found in the SVG file '%s': %s" % (component.name, len(reaction_component)))
    print ("Metabolites found in the SVG file '%s': %s" % (component.name, len(metabolite_component)))
    print ("Enzymes found in the SVG file '%s': %s" % (component.name, len(enzyme_component)))
    print ("Subsystem found in the SVG file '%s': %s" % (component.name, len(subsystem_component)))

    compt_rme_svg = {
        'reaction': {e for e in reaction_component},
        'metabolite': {e for e in metabolite_component},
        'enzyme': {e for e in enzyme_component}
    }
    compt_sub_svg = None
    if isinstance(component, CompartmentSvg):
        compt_sub_svg = set()
        for s in subsystem_component:
            compt_sub_svg.add(s)

    return compt_rme_svg, compt_sub_svg


def insert_compartment_svg_connectivity_and_stats(database, compartment, map_directory):
    # compartment svg stats, values correspond to what is inside the svg files and might difer from the model
    # so:
    # 1) make sure the maps are valid using validation files provided with the Omix plugin
    # 2) whenever svg files change, run this again
    compt_rme_svg, compt_sub_svg = parse_svg(database, compartment, map_directory)

    rcs = ReactionComponent.objects.using(database).filter(id__in=compt_rme_svg['metabolite'])
    for rc in rcs:
        add = ReactionComponentCompartmentSvg(rc=rc, compartmentsvg=compartment)
        add.save(using=database)
    metabolite_count = rcs.count()
    unique_meta = set()
    for met in rcs:
        unique_meta.add(met.id[:-1])
    unique_meta_count = len(unique_meta)

    # add the connection to the reactions
    rs = Reaction.objects.using(database).filter(id__in=compt_rme_svg['reaction'])
    for r in rs:
        add = ReactionCompartmentSvg(reaction=r, compartmentsvg=compartment)
        add.save(using=database)
    reaction_count = rs.count()

    rcs = ReactionComponent.objects.using(database).filter(id__in=compt_rme_svg['enzyme'])
    for rc in rcs:
        add = CompartmentSvgEnzyme(rc=rc, compartmentsvg=compartment)
        add.save(using=database)
    enzyme_count  = rcs.count()

    subs = Subsystem.objects.using(database).filter(name__in=compt_sub_svg)
    for sub in subs:
        add = SubsystemCompartmentSvg(subsystem=sub, compartmentsvg=compartment)
        add.save(using=database)
    subsystem_count = subs.count()

    if reaction_count == 0 or metabolite_count == 0 or unique_meta_count == 0 or enzyme_count == 0 or subsystem_count == 0:
        print ("Error: compartment '%s'" % subsystem.filename)
        print("reaction_count", reaction_count)
        print("metabolite_count", metabolite_count)
        print("unique metabolite_count", unique_meta_count)
        print("enzyme_count", enzyme_count)
        print("subsystem_count", subsystem_count)

    CompartmentSvg.objects.using(database). \
        filter(id=compartment.id).update(reaction_count=reaction_count, subsystem_count=subsystem_count, \
         metabolite_count=metabolite_count, unique_metabolite_count=unique_meta_count, enzyme_count=enzyme_count)


def insert_subsystem_svg_connectivity_and_stats(database, subsystem, map_directory):
    # subsystem svg stats, values correspond to what is inside the svg files and might difer from the model
    sub_rme_svg, sub_sub_svg = parse_svg(database, subsystem, map_directory)

    rcs = ReactionComponent.objects.using(database).filter(id__in=sub_rme_svg['metabolite'])
    for rc in rcs:
        add = ReactionComponentSubsystemSvg(rc=rc, subsystemsvg=subsystem)
        add.save(using=database)
    metabolite_count = rcs.count()
    unique_meta = set()
    for met in rcs:
        unique_meta.add(met.id[:-1])
    unique_meta_count = len(unique_meta)

    # add the connection to the reactions
    rs = Reaction.objects.using(database).filter(id__in=sub_rme_svg['reaction'])
    for r in rs:
        add = ReactionSubsystemSvg(reaction=r, subsystemsvg=subsystem)
        add.save(using=database)
    reaction_count = rs.count()

    rcs = ReactionComponent.objects.using(database).filter(id__in=sub_rme_svg['enzyme'])
    for rc in rcs:
        add = SubsystemSvgEnzyme(rc=rc, subsystemsvg=subsystem)
        add.save(using=database)
    enzyme_count  = rcs.count()

    if reaction_count == 0 or metabolite_count == 0 or unique_meta_count == 0 or enzyme_count == 0:
        print ("Error: subsystem '%s'" % subsystem.filename)
        print("reaction_count", reaction_count)
        print("metabolite_count", metabolite_count)
        print("unique metabolite_count", unique_meta_count)
        print("enzyme_count", enzyme_count)

    # TODO save compartment count?
    SubsystemSvg.objects.using(database). \
        filter(id=subsystem.id).update(reaction_count=reaction_count, \
         metabolite_count=metabolite_count, unique_metabolite_count=unique_meta_count, enzyme_count=enzyme_count)


def compare_database_and_svg(compt_rme_svg, compt_rme, compt_sub_svg):
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




def processData(database, map_type, map_directory, svg_map_metadata_file):
    # insert svg metadata
    if map_type == 'compartment':
        with open(svg_map_metadata_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for ci in reader:
                if not ci or ci[0][0] == '#':
                    continue
                compt = Compartment.objects.using(database).filter(name__iexact=ci[1])
                if not compt:
                    print("Error: cannot match the compartment name " + ci[1] + " to a compartment in the database")
                    exit(1)

                if not re.match('[0-9a-zA-Z_]+[.]svg$', ci[3]):
                    print("invalid file name %s, expected to match [0-9a-zA-Z_]+[.]svg$")
                    exit(1)

                inDB = False
                try:
                    cinfo = CompartmentSvg.objects.using(database).get(name_id=ci[0])
                    inDB = True
                except CompartmentSvg.DoesNotExist:
                    cinfo = CompartmentSvg(name=ci[2], name_id=ci[0], compartment=compt[0], filename=ci[3], letter_code=ci[4])
                    cinfo.save(using=database)

                svg_path = os.path.join(map_directory, ci[3])
                if not os.path.isfile(svg_path):
                    print("Warning: file '" + svg_path + "' not found")
                    CompartmentSvg.objects.using(database). \
                        filter(id=cinfo.id).update(sha=None, reaction_count=0, subsystem_count=0, \
                         metabolite_count=0, unique_metabolite_count=0, enzyme_count=0)
                    continue

                # get sha
                sha = hashlib.sha256(file_as_bytes(open(svg_path, 'rb'))).hexdigest()
                if sha != cinfo.sha:
                    CompartmentSvg.objects.using(database).filter(id=cinfo.id).update(sha=sha)
                    insert_compartment_svg_connectivity_and_stats(database, cinfo, map_directory)
                else:
                    print("SVG file '%s' is unchanged" % ci[3])

    elif map_type == 'subsystem':
        with open(svg_map_metadata_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for si in reader:
                if not si or si[0][0] == '#':
                    continue
                sub = Subsystem.objects.using(database).filter(name_id=si[1])
                if not sub:
                    print("Error: cannot match the subsystem  name " + si[1] + " to a subsystem in the database")
                    exit(1)

                if not re.match('[0-9a-zA-Z_]+[.]svg$', si[3]):
                    print("invalid file name %s, expected to match [0-9a-zA-Z_]+[.]svg$")
                    exit(1)

                inDB = False
                try:
                    sinfo = SubsystemSvg.objects.using(database).get(name_id=si[0])
                    inDB = True
                except SubsystemSvg.DoesNotExist:
                    sinfo = SubsystemSvg(name_id=si[0], subsystem=sub[0], name=si[2], filename=si[3])
                    sinfo.save(using=database)

                svg_path = os.path.join(map_directory, si[3])
                if not os.path.isfile(svg_path):
                    print("Warning: file '" + svg_path + "' not found")
                    SubsystemSvg.objects.using(database). \
                        filter(id=sinfo.id).update(sha=None, reaction_count=0, compartment_count=0, \
                         metabolite_count=0, unique_metabolite_count=0, enzyme_count=0)
                    continue

                # get sha
                sha = hashlib.sha256(file_as_bytes(open(svg_path, 'rb'))).hexdigest()
                if sha != sinfo.sha:
                    SubsystemSvg.objects.using(database).filter(id=sinfo.id).update(sha=sha)
                    insert_subsystem_svg_connectivity_and_stats(database, sinfo, map_directory)
                else:
                    print("SVG file '%s' is unchanged" % si[3])


class Command(BaseCommand):

    def add_arguments(self, parser):
        import argparse
        parser.add_argument('database', type=str)
        parser.add_argument('map type', type=str, choices=['compartment', 'subsystem'], help="'compartment' or 'subsystem'")
        parser.add_argument('map directory', type=str, help="location of the svg files")
        parser.add_argument('map metadata file', type=str,
            help="tabular file that describes the name_id/name/letter/.... of the maps")
        parser.add_argument('--write-connectivity-files', action="store_true", default=False, dest='write_connectivity',
            help="Find and write overlaps between compt/sub/reaction/meta into files")
        parser.add_argument('--delete-compartment-tables', action="store_true", default=False, dest='delete_compartment_tables',
            help="delete the content of 'svg' compartment tables and quit")
        parser.add_argument('--delete-subsystem-tables', action="store_true", default=False, dest='delete_subsystem_tables',
            help="delete the content of 'svg' subsystem tables and quit")


    def handle(self, *args, **options):
        if options['delete_compartment_tables']:
            CompartmentSvg.objects.using(options['database']).all().delete()
            ReactionCompartmentSvg.objects.using(options['database']).all().delete()
            ReactionComponentCompartmentSvg.objects.using(options['database']).all().delete()
            SubsystemCompartmentSvg.objects.using(options['database']).all().delete()
            return

        if options['delete_subsystem_tables']:
            SubsystemSvg.objects.using(options['database']).all().delete()
            ReactionSubsystemSvg.objects.using(options['database']).all().delete()
            ReactionComponentSubsystemSvg.objects.using(options['database']).all().delete()
            return

        if options['write_connectivity']:
            # get element in subsystem / compt from database
            compt_rme, rme_compt, sub_rme, rme_sub, compt_sub, sub_compt_using_reaction, \
             compt_sub_reaction, pathway_compt_coverage = get_components_interconnection(options['database'])

            get_compt_subsystem_connectivity(options['database'], options['map directory'], compt_rme, rme_compt, sub_rme, rme_sub, compt_sub, compt_sub_reaction, pathway_compt_coverage)

            # get element in subsystem / compt from svg
            compt_rme_svg, rme_compt_svg, compt_sub_svg, sub_compt_svg = get_subsystem_compt_element_svg_global(options['database'], options['map directory'])
            write_subsystem_summary_file(options['database'], rme_compt_svg, sub_compt_svg, pathway_compt_coverage)
            return

        processData(options['database'], options['map type'], options['map directory'], options['map metadata file'])
