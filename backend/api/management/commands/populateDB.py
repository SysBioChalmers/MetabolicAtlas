import sys, os, importlib ,logging, re, csv, collections

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand
import xml.etree.ElementTree as etree
import libsbml

logger = logging.getLogger(__name__)
sh = logging.StreamHandler(stream=sys.stderr)
logger.addHandler(sh)
formatter = logging.Formatter(("%(asctime)s - %(name)s - %(levelname)s - "
                               "%(message)s"))
sh.setFormatter(formatter)
logger.setLevel(logging.INFO)

verbose=False;  # dont print the error messages from the addReactionComponentAnnotation
annotationsToAdd = {}

exec(open(os.path.join(sys.path[0], "../", "database_generation", "addSBMLData.py")).read())
exec(open(os.path.join(sys.path[0], "../", "database_generation", "addCurrencyMetabolites.py")).read())
exec(open(os.path.join(sys.path[0], "../", "database_generation", "addMetabolites.py")).read())
exec(open(os.path.join(sys.path[0], "../", "database_generation", "addReactionComponentAnnotation.py")).read())
exec(open(os.path.join(sys.path[0], "../", "database_generation", "addEnzymes.py")).read())

# this is a "wrapper" file that will simply call each and every one of the add files, in the RIGHT order...
# 1) addSBMLData ../database_generation/data/HMRdatabase2_00.xml 67
# 2) addCurrencyMetabolites
# 3) addMetabolites
# 4) addReactionComponentAnnotation ../database_generation/data/ensembl82_uniprot_swissprot.tab ensg 0 uniprot  1
#    addReactionComponentAnnotation ../database_generation/data/uniprot.human.keywords.tab uniprot 1 up_keywords  2
# 5) addEnzymes

# where are the data located?
baseFolder="/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/"

# the human files and the yeast files are obviously different :)
# so wrap up all the files for the given species
def populate_human_db():
    # first check that ALL files exists
    missingFiles = 0
    missingFiles+=_checkIfFileExists("HMRdatabase2_00.xml")
    missingFiles+=_checkIfFileExists("human_currencyMets.csv")
    missingFiles+=_checkIfFileExists("human_massCalc.txt")
    missingFiles+=_checkIfFileExists("human_metaboliteListFromExcel.txt")
    missingFiles+=_checkIfFileExists("hmdb.tab")
    missingFiles+=_checkIfFileExists("ensembl82_uniprot_swissprot.tab")
    missingFiles+=_checkIfFileExists("uniprot.human.keywords.tab")
    missingFiles+=_checkIfFileExists("uniprot.human.EC.tab")
    missingFiles+=_checkIfFileExists("uniprot.human.function.tab")
    missingFiles+=_checkIfFileExists("uniprot.human.CatalyticActivity.tab")
    missingFiles+=_checkIfFileExists("human.kegg.tab")
    missingFiles+=_checkIfFileExists("uniprot.human.names.tab")
    if missingFiles>0:
        sys.exit("At least one missing annotation file, see above for specifications, will not attempt to add any data to the database...")

    # then add the data to the database in the RIGHT order
    addSBMLData(baseFolder+"HMRdatabase2_00.xml", 67, None)                 # addSBMLData
    logger.info("Currency Metabolites")
    addCurrencyMetabolites(baseFolder+"human_currencyMets.csv")         # addCurrencyMetabolites
    # addMetabolites
    logger.info("Add annotations for the metabolites")
    masses = readMassCalcFile(baseFolder+"human_massCalc.txt")
    hmdb = readHMDBFile(baseFolder+"hmdb.tab")
    metaboliteDefinitions(baseFolder+"human_metaboliteListFromExcel.txt", masses, hmdb)
    # addReactionComponentAnnotation
    logger.info("Add 'mappings' between identifiers")
    addReactionComponentAnnotation("ensg", 0, "uniprot",
        baseFolder+"ensembl82_uniprot_swissprot.tab", 1)
    addReactionComponentAnnotation("uniprot", 1, "up_keywords",
        baseFolder+"uniprot.human.keywords.tab", 2)
    # addEnzymes
    logger.info("Add annotations for the proteins")
    ec = readAnnotationFile(baseFolder+"uniprot.human.EC.tab")
    function = readAnnotationFile(baseFolder+"uniprot.human.function.tab")
    activity = readAnnotationFile(baseFolder+"uniprot.human.CatalyticActivity.tab")
    kegg = readAnnotationFile(baseFolder+"human.kegg.tab")
    addEnzymes(baseFolder+"uniprot.human.names.tab", ec, function, activity, kegg)


def populate_yeast_db():
    # first check that ALL files exists
    missingFiles = 0
    missingFiles+=_checkIfFileExists("yeast76.xml")
    if missingFiles>0:
        sys.exit("At least one missing annotation file, see above for specifications, will not attempt to add any data to the database...")
    addSBMLData(baseFolder+"yeast76.xml", 2017, "http://yeastgenome.org/")


def _checkIfFileExists(fName):
    if not os.path.isfile(baseFolder+fName):
        print("Missing the file "+baseFolder+fName)
        return(1)
    return(0)



class Command(BaseCommand):

    def handle(self, *args, **options):
        #populate_human_db()
        populate_yeast_db()
        # until Dimitra have added the annotations to the SBML file...
        pmids_to_add = {}
        with open(baseFolder+"human_reactionsFromExcel.txt", 'r') as f:
            next(f) # skip the header
            for line in f:
                tokens = line.strip().split("\t")
                reaction_id = tokens[0]
                if(len(tokens)>16):
                    refs = tokens[16]
                    refs = refs.replace('"', '')
                    r = refs.split(";")
                    reaction = Reaction.objects.filter(id="R_"+reaction_id)
                    if(len(reaction)<1):
                        print("No reaction found with id "+"R_"+reaction_id)
                        next;
                    for pmid in r:
                        if(re.match(r'PMID', pmid)): # skip the uniprot entry records???
                            rr = ReactionReference(reaction=reaction[0], pmid=pmid)
                            if len(pmid)>25:
                                print("PMID is "+pmid)
                            pmids_to_add[str(rr)] = rr
                else:
                    #print("No references found for reaction "+reaction_id)
                    #do nothing atm
                    a = 1
        #ReactionReference.objects.bulk_create(pmids_to_add.values())
