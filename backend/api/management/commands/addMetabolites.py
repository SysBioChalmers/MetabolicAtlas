import sys, os, csv

from django.db import models
from api.models import Metabolite, ReactionComponent

from django.core.management.base import BaseCommand


#metaboliteListFromExcel
##	METID	METNAME	UNCONSTRAINED	MIRIAM	COMPOSITION	InChI	COMPARTMENT	REPLACEMENT ID	LM_ID	SYSTEMATIC_NAME	SYNONYMS	BIGG ID	EHMN ID	CHEBI_ID	CHEBI_ID	KEGG_ID	HMDB_ID	HepatoNET ID
def metaboliteDefinitions(fileName, hmdbMasses, hmdbInfo):
    mets = []
    with open(fileName, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        next(f) # skip the header
        for row in reader:
            reaction_component_id = row[8]
            if(row[0]!="#"):
                if(len(reaction_component_id)>1):
                    reaction_component_id = "M_"+reaction_component_id
                    reaction_component = ReactionComponent.objects.filter(id=reaction_component_id)
                    if(len(reaction_component)<1):
                        print("No reaction component found with id "+reaction_component_id)
                        sys.exit()
                    hmdb = row[17]
                    hmdb_link = None;
                    mass = None; formula = None; avg_mass = None;
                    hmdb_name = None; hmdb_desc = None; hmdb_function = None;
                    if(len(hmdb)>0):
                        hmdb_link = "http://www.hmdb.ca/metabolites/"+hmdb
                        if(hmdb in hmdbMasses):
                            current = hmdbMasses[hmdb]
                            formula = current["formula"]
                            mass = current["weight"]
                            avg_mass = current["avg_weight"]
                        if(hmdb in hmdbInfo):
                            current = hmdbInfo[hmdb]
                            hmdb_name = current["name"]
                            hmdb_desc = current["description"]
                            hmdb_function = current["function"]
                        else:
                            print("a HMDB id, "+hmdb+" which was not found in the HMDB database!!!")
                    pubchem_link = None
                    pubchem_link = "https://pubchem.ncbi.nlm.nih.gov/compound/"+reaction_component[0].long_name
                    kegg = row[16]
                    chebi = row[14]
                    inchi = row[6]
                    bigg = row[12]
                    m = Metabolite(reaction_component=reaction_component[0], hmdb=hmdb,
                        formula=formula, mass=mass, mass_avg=avg_mass, kegg=kegg,
                        chebi=chebi, inchi=inchi, bigg=bigg,
                        hmdb_link=hmdb_link, pubchem_link=pubchem_link,
                        hmdb_name=hmdb_name, hmdb_description=hmdb_desc,
                        hmdb_function=hmdb_function)
                    mets.append(m)
                else:
                    print("No reaction_component_id found on line starting with "+row[0]+" and "+row[1])
    Metabolite.objects.bulk_create(mets)


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


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'
    folder="/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/"
    massFile=folder+"massCalc.txt"
    annFile=folder+"metaboliteListFromExcel.txt"
    hmdbFile=folder+"hmdb.tab"

    def handle(self, *args, **options):
        masses = readMassCalcFile(self.massFile)
        hmdb = readHMDBFile(self.hmdbFile)
        metaboliteDefinitions(self.annFile, masses, hmdb)
