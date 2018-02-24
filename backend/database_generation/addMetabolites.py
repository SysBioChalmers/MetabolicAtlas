import csv
from api.models import *
import sqlite3
import re

######################################################################
# the actual code to read and import annotations for the metabolites #
######################################################################


#metaboliteListFromExcel
##	METID	METNAME	UNCONSTRAINED	MIRIAM	COMPOSITION
##	InChI	COMPARTMENT	REPLACEMENT ID	LM_ID	SYSTEMATIC_NAME
##	SYNONYMS	BIGG ID	EHMN ID	CHEBI_ID	CHEBI_ID
##	KEGG_ID	HMDB_ID	HepatoNET ID

# TODO
# put checking into methodes
# add cross check with CHEBI database
# add cross check with lipidMaps if ..
# get and check Kegg ID from pubchem synonym 
def metaboliteDefinitions(database, fileName, hmdb_data, pubchem_db, lipidmaps_data, skip_first_metabolite=0):

    def match(expr, item):
        return re.match(expr, item) is not None

    reannotate = False
    if reannotate:
        con = sqlite3.connect(pubchem_db)
        con.create_function("REGEXP", 2, match)
        cur = con.cursor()

    # store all names to compare with new name found in pubchem/hmdb
    rc_name_dict = {}
    reaction_component = ReactionComponent.objects.using(database).all()
    for rc in reaction_component:
        rc_name_dict[rc.short_name] = rc.short_name

    with open(fileName, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        next(f) # skip the header
        HMDB_dict, HMDB_secondary_dict, HMDB_name_dict, HMDB_iupac_name_dict, HMDB_synonyms_dict, \
         HMDB_chebi_dict, HMDB_pubchem_dict = hmdb_data
        '''LIPIDMAPS_dict, LIPIDMAPS_name_dict, LIPIDMAPS_systematic_name_dict, \
         LIPIDMAPS_synonyms_dict, LIPIDMAPS_chebi_dict, LIPIDMAPS_pubchem_dict, \
         LIPIDMAPS_hmdb_dict = lipidmaps_data'''

        prev_name = None
        inserted = 0
        inserted_hmdb = 0
        i = 0
        for i, row in enumerate(reader):
            # print (row)
            if i < skip_first_metabolite:
                continue

            if i != 0 and i % 100 == 0:
                print ("Processing metabolite", i)

            reaction_component_id = row[8]
            if row[0] and row[0][0] == "#":
                continue

            if not reaction_component_id:
                print ("Error: empty reaction_component_id, cannot process", row[1])
                exit(1)

            reaction_component_id = "M_"+reaction_component_id # TODO remove M_?
            reaction_component = ReactionComponent.objects.using(database).filter(id=reaction_component_id)
            if not reaction_component:
                print("Error: no reaction component found with id "+reaction_component_id)
                exit(1)
            reaction_component = reaction_component[0]
            rc_name = reaction_component.short_name
            rc_long_name = reaction_component.long_name
            if rc_name != rc_long_name:
                print ("Error: %s != %s " % (rc_name, rc_long_name))
                exit(1)

            m = Metabolite.objects.using(database).filter(reaction_component=reaction_component, )
            if m:
                continue

            hmdb_id = row[17]
            if not hmdb_id:
                hmdb_id = None
            hmdb_link = None
            mass = None; formula = None; avg_mass = None;
            hmdb_name = None; hmdb_desc = None; hmdb_function = None;
            pubchem_link = None

            kegg = row[16] if row[16] else None
            chebi = row[14].lstrip("CHEBI:") if row[14] else None
            inchi = row[6] if row[6] else None
            bigg = row[12] if row[12] else None
            if reannotate:
                bigg = None # FIXME forget about bigg id now

            pubchem_id = None
            pubchem_hmdb_id = None
            correct_pubchem_id = None
            xls_hmdb_not_found = False
            hmdb_id_name_fix = False
            correct_pubchem_name = None
            correct_re_name = None
            correct_name = None
            pubchem_chebi = None
            pubchem_kegg = None

            if reannotate:
                if HMDB_dict and HMDB_synonyms_dict and hmdb_id and \
                    hmdb_id not in HMDB_dict and hmdb_id.lower() not in HMDB_synonyms_dict:
                    hmdb_id = None
                    print("Warning: HMDB ID '%s' not found in the HMDB database!!!" % hmdb_id)
                    xls_hmdb_not_found = True

                cur.execute("SELECT * FROM alias WHERE alias='%s' and pos=1" % rc_name.replace('\'', '\'\''))
                res = cur.fetchall()
                '''if not res:
                    cur.execute("SELECT * FROM alias WHERE alias='%s' and pos < 4" % rc_name.replace('\'', '\'\''))
                    res2 = cur.fetchall()
                    if len(res2) == 1:
                        res = res2
                        if res[0][2] != 1:  # position of the name in the synonym, 1 == best
                            # select a better name for this metabolite
                            CID = res[0][1]
                            cur.execute("SELECT * FROM alias WHERE cid=%s and pos=1" % CID)
                            res2 = cur.fetchall()
                            correct_pubchem_name = res2[0][0]'''

                if not res:
                    # try without () around 10Z for instance
                    name = re.sub('(.*)[(](\d+[RSEZ](?:(?:,\d+[RSEZ])+)?)[)](.*)', '\g<1>\g<2>\g<3>', rc_name)
                    name = re.sub('(.*)([(][RSEZ][)])[,](.*)', '\g<1>\g<2>-\g<3>', name)
                    cur.execute("SELECT * FROM alias WHERE alias='%s'" % (name.replace('\'', '\'\'')))
                    res2 = cur.fetchall()
                    if len(res2) == 1:
                        res = res2
                        correct_re_name = name

                if correct_re_name or correct_pubchem_name:
                    correct_name = correct_re_name or correct_pubchem_name
                if res:
                    if len(res) > 1:
                        print ("Warning: multiple pubchem entry match")
                        print (res)
                    else:
                        pubchem_id = str(res[0][1])
                        # get the HDMB from the CID
                        if pubchem_id in HDMB_pubchem:
                            pubchem_hmdb_id = HDMB_pubchem[pubchem_id]
                            if len(pubchem_hmdb_id) > 1:
                                if correct_name:
                                    # try to fix using the corrected name
                                    for el in pubchem_hmdb_id:
                                        if HMDB_dict[el]["name"].lower() == correct_name.lower():
                                            pubchem_hmdb_id = [el]

                            if len(pubchem_hmdb_id) > 1:
                                if HMDB_synonyms_dict and correct_name:
                                    # discard the one not matching synonyms
                                    pubchem_hmdb_id = [e for e in pubchem_hmdb_id if correct_name.lower() in
                                     [s.lower() for s in HMDB_dict[e]["synonyms"]]]
                                    print (pubchem_hmdb_id)
                                    if len(pubchem_hmdb_id) > 1:
                                        print ("Warning: multiple HMDB entry match pubchem id %s : %s - %s" %
                                         (pubchem_id, pubchem_hmdb_id, rc_name))
                                        pubchem_id = None
                            else:
                                pubchem_hmdb_id = pubchem_hmdb_id[0]
                            if not hmdb_id:
                                hmdb_id = pubchem_hmdb_id

                        if pubchem_id:
                            #check if a CHEBI and KEGG ID are available
                            cur.execute("SELECT * FROM alias WHERE cid=%s and alias like 'CHEBI%%'" % pubchem_id)
                            res = cur.fetchall()
                            if res:
                                pubchem_chebi = res[0][0].lstrip("CHEBI:")

                             #check if a CHEBI and KEGG ID are available
                            cur.execute("SELECT * FROM alias WHERE cid=%s and alias REGEXP 'C[0-9]{5}'" % pubchem_id)
                            res = cur.fetchall()
                            if res:
                                pubchem_kegg = res[0][0]

                # try to get the data from HMDB using the name
                name2 = re.sub('(.*)[(](\d+[A-Z](?:(?:,\d+[A-Z])+)?)[)](.*)', '\g<1>\g<2>\g<3>', rc_name)
                name2 = re.sub('(.*)([(][RSEZ][)])[,](.*)', '\g<1>\g<2>-\g<3>', name2)
                # look in the HMDB_name dict first
                HMDB_id_short_name = HMDB_name_dict[rc_name.lower()] if rc_name.lower() in HMDB_name_dict else None
                HMDB_id_corrected_name = HMDB_name_dict[name2.lower()] if name2.lower() in HMDB_name_dict else None
                if not HMDB_id_short_name and not HMDB_id_corrected_name:
                    # look in the iupac_name dict
                    HMDB_id_short_name = HMDB_iupac_name_dict[rc_name.lower()] if rc_name.lower() in HMDB_iupac_name_dict else None
                    HMDB_id_corrected_name = HMDB_iupac_name_dict[name2.lower()] if name2.lower() in HMDB_iupac_name_dict else None

                if not HMDB_id_short_name and not HMDB_id_corrected_name:
                    # look in the iupac_name dict
                    HMDB_id_short_name = HMDB_synonyms_dict[rc_name.lower()] if rc_name.lower() in HMDB_synonyms_dict else None
                    HMDB_id_corrected_name = HMDB_synonyms_dict[name2.lower()] if name2.lower() in HMDB_synonyms_dict else None

                # print (HMDB_id_short_name)
                # print (HMDB_id_corrected_name)

                if HMDB_id_short_name or HMDB_id_corrected_name:
                    if HMDB_id_short_name and HMDB_id_corrected_name:
                        if HMDB_id_short_name != HMDB_id_corrected_name:
                            # try to fix if one match the exact name
                            if len(HMDB_id_short_name) == 1 and len(HMDB_id_corrected_name) == 1:
                                if HMDB_dict[HMDB_id_short_name[0]]["name"].lower() in [name2.lower(), rc_name.lower()]:
                                    HMDB_id_corrected_name = None
                                elif HMDB_dict[HMDB_id_corrected_name[0]]["name"].lower() in [name2.lower(), rc_name.lower()]:
                                    HMDB_id_short_name = None
                                    hmdb_id_name_fix = name2

                        if HMDB_id_short_name and HMDB_id_corrected_name and HMDB_id_short_name != HMDB_id_corrected_name:
                            print ("Error: HMDB_id_short_name %s != HMDB_id_corrected_name %s" % 
                                (rc_name, name2))
                            print (HMDB_id_short_name, HMDB_id_corrected_name)
                            exit(1)

                        if hmdb_id_name_fix and correct_name and hmdb_id_name_fix != correct_name:
                            print ("Error: HMDB_id_corrected %s != hmdb_id_name_fix %s" % 
                                (hmdb_id_name_fix, correct_name))
                            exit(1)

                    HMDB_name = HMDB_id_short_name or HMDB_id_corrected_name
                    if len(HMDB_name) != 1:
                        # check if one of entry matches the name not the synonym
                        for r in HMDB_name:
                            if HMDB_dict[r]["name"].lower() in [name2.lower(), rc_name.lower()]:
                                HMDB_name = [r]
                                break
                        if len(HMDB_name) != 1 and not hmdb_id:
                            # FIXME? the hmdb_id might be wrong at the step
                            print ("Error multi HMDB found using names: %s, %s" % (HMDB_name, name2))
                            print ("selecting the most recent ID (higher) is less than 5")
                            multiple_HMDB = HMDB_name
                            HMDB_name = None
                            '''if len(HMDB_name) < 5:
                                hid = 0
                                HMDB_ID = None
                                for r in HMDB_name:
                                    phid = int(r[4:])
                                    if phid > hid:
                                        hid = phid
                                        HMDB_ID = r
                                HMDB_name = [HMDB_ID]
                            else:
                                HMDB_name = None'''
                            #exit(1)

                    if HMDB_name:
                        HMDB_name = HMDB_name[0]
                        if not hmdb_id and not pubchem_hmdb_id:
                            print ("Warning: no HMDB id in excel file but %s is in HMDB_synonyms_dict for %s" % 
                                (HMDB_name, rc_name))
                            hmdb_id = HMDB_name
                        elif hmdb_id and pubchem_hmdb_id != hmdb_id:
                            if hmdb_id != HMDB_name:
                                print ("Warning: xls id %s != HMDB_name %s" % (hmdb_id, HMDB_name))
                                if hmdb_id in HMDB_dict[HMDB_name]["sec_accession"]:
                                    hmdb_id = HMDB_name
                                elif hmdb_id_name_fix:
                                    hmdb_id = HMDB_name
                                else:
                                    print ("Error: xls id %s != HMDB_name %s - %s" % (hmdb_id, HMDB_name, name2))
                                    for k ,v in HMDB_dict[HMDB_name].items():
                                        print (k, v)
                                    exit(1)
                        elif HMDB_name != pubchem_hmdb_id:
                             print ("Warning: HMDB_synonyms_dict is %s but hmdb found with pubchem is %s for %s (pubchem %s)" % 
                                (HMDB_name, pubchem_hmdb_id, rc_name, pubchem_id))
                             # keep the HMDB, and keep the correct(?) pubchem_id
                             correct_pubchem_id = pubchem_id
                             hmdb_id = HMDB_name

                # make esure the corrected name is unique among metabolite
                if correct_name:
                    print ("corrected name %s was %s" % (correct_name, rc_name))
                    if prev_name != rc_name and correct_name != rc_name:
                        if correct_name in rc_name_dict:
                            print ("Error name '%s' already used for a metabolite, rc name: %s" % (correct_name, rc_name))
                            print ("use for %s" % rc_name_dict[correct_name])
                            print (correct_pubchem_name, correct_re_name)
                            exit(1)
                    rc_name_dict[correct_name] = rc_name
                prev_name = rc_name

            if hmdb_id:
                if hmdb_id not in HMDB_dict:
                    if hmdb_id.lower() in HMDB_synonyms_dict:
                        # print("Warning: ID '%s' found in sec accession/synonym dict as %s" % (hmdb_id, HMDB_synonyms_dict[hmdb_id]))
                        hmdb_id = HMDB_synonyms_dict[hmdb_id.lower()]
                        if len(hmdb_id) > 1:
                            print ("Error: multi HMDB id match", hmdb_id)
                            exit(1)
                        else:
                            hmdb_id = hmdb_id[0]
                    else:
                        if pubchem_hmdb_id: # test this before HMDB_synonyms_dict?
                            hmdb_id = pubchem_hmdb_id
                        else:
                            print("Warning: ID '%s' not valid" % hmdb_id)
                            hmdb_id = None

                    if pubchem_hmdb_id and pubchem_hmdb_id != hmdb_id:
                        # if xls_hmdb_not_found:
                        #    hmdb_id = pubchem_hmdb_id
                        #else:
                        print ("Error: HMDB id using pubchem id: %s != xls is %s" % (pubchem_hmdb_id, hmdb_id))
                        exit(1)

                if hmdb_id:
                    hmdb_link = "http://www.hmdb.ca/metabolites/%s" % hmdb_id

                if hmdb_id and hmdb_id in HMDB_dict:
                    current = HMDB_dict[hmdb_id]
                    hmdb_name = current["name"]
                    hmdb_desc = current["description"]
                    hmdb_function = current["functions"]
                    formula = current["formula"]
                    mass = current["mono_weight"]
                    avg_mass = current["avg_weight"]

                    if current["pubchem"]: # use pubchem_link ID
                        if pubchem_id and current["pubchem"] and pubchem_id != current["pubchem"]:
                            print ("warning: missmatch pubchem db id %s vs HMDB pubchem %s" % (pubchem_id, current["pubchem"]))
                            print ("pubchem db id selected")
                        else:
                            pubchem_id = current["pubchem"]

                    if pubchem_id:
                        pubchem_link = "https://pubchem.ncbi.nlm.nih.gov/compound/%s" % pubchem_id
                elif reannotate:
                    print("not possible")
                    exit(1)

            if reannotate:
                if correct_pubchem_id:
                    pubchem_id = correct_pubchem_id
                if pubchem_id:
                    pubchem_link = "https://pubchem.ncbi.nlm.nih.gov/compound/%s" % pubchem_id

                if hmdb_id and hmdb_id in HMDB_dict:
                    hmdb_kegg = HMDB_dict[hmdb_id]["kegg"]
                    hmdb_chebi = HMDB_dict[hmdb_id]["chebi"]
                    hmdb_inchi = HMDB_dict[hmdb_id]["inchi"]


                kegg_ids = [el for el in [kegg, hmdb_kegg, pubchem_kegg] if el]
                chebi_ids = [el for el in [chebi, hmdb_chebi, pubchem_chebi] if el]
                inchi_ids = [el for el in [inchi, hmdb_inchi] if el]

                kegg_ids_set = set(kegg_ids)
                chebi_ids_set = set(chebi_ids)
                inchi_ids_set = set(inchi_ids)

                if len(kegg_ids_set) > 1:
                    print ("Warning, kegg ids found are different: %s " % kegg_ids)
                    print ("abort insert %s (%s)" % (rc_name, correct_name))
                    if correct_name:
                        del rc_name_dict[correct_name]
                    continue
                elif kegg_ids_set:
                    kegg = next(iter(kegg_ids_set))

                if len(chebi_ids_set) > 1:
                    print ("Warning, chebi ids found are different: %s " % chebi_ids)
                    print ("abort insert %s (%s)" % (rc_name, correct_name))
                    if correct_name:
                        del rc_name_dict[correct_name]
                    continue
                elif chebi_ids_set:
                    chebi = next(iter(chebi_ids_set))

                if len(inchi_ids_set) > 1:
                    print ("Warning, inchi ids found are different: %s " % inchi_ids)
                    print ("abort insert %s (%s)" % (rc_name, correct_name))
                    if correct_name:
                        del rc_name_dict[correct_name]
                    continue
                elif inchi_ids_set:
                    inchi = next(iter(inchi_ids_set))

            inserted += 1
            if hmdb_id:
                inserted_hmdb += 1
            # print (row[1], rc_name, correct_name, hmdb_id, kegg, chebi, pubchem_id, inchi[:10] if inchi else inchi, formula)
            # exit(1)

            # FIXME Remove the 'charge' field in the model, not used
            m = Metabolite(reaction_component=reaction_component, hmdb=hmdb_id,
                formula=formula, mass=mass, mass_avg=avg_mass, kegg=kegg,
                chebi=chebi, inchi=inchi, bigg=bigg,
                hmdb_link=hmdb_link, pubchem_link=pubchem_link,
                hmdb_name=hmdb_name, hmdb_description=hmdb_desc,
                hmdb_function=hmdb_function)
            m.save(using=database)

            # check formula
            if reaction_component.formula != formula and not reaction_component.formula:
                # TODO maybe replace the current formula
                reaction_component.formula = formula
                reaction_component.save(using=database)

            if correct_name:
                # TODO replace the metabolic name
                # and replace the name in the reaction equation
                pass

    if reannotate:
        cur.close()
        con.close()

    print ("inserted %s / %s" % (inserted, i))
    print ("inserted hmdb %s" % inserted_hmdb)


    # with reannotate
    # inserted 4605 / 6008
    # inserted hmdb 2796

    # without
    # inserted 6006 / 6008
    # inserted hmdb 1435



#HMDB_ID;Name;Formula;Monoisotopic Molecular Weight (exact_mass);Average Molecular Weight
def readMassCalcFile(filename):
    with open(filename, "r") as f:
        reader = csv.reader(f, delimiter=';')
        next(f) # skip the header
        masses = {}
        for row in reader:
            m = {"formula":row[2], "weight":row[3], "avg_weight":row[4]};
            masses[row[0]] = m
    return masses

def readHMDBFile(fileName):
    with open(fileName, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        next(f) # skip the header
        hmdb_info = {}
        for row in reader:
            h = {"name":row[1], "description":row[2], "function":row[3]};
            hmdb_info[row[0]] = h
    return hmdb_info
