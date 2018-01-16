import sys, os, importlib ,logging, re, csv, collections

# add db generation files to path
sys.path.insert(0, "/project/database_generation/")
sys.path.insert(0, "/project/related_scripts/create_the_import_files/")
import addSBMLData
import addCurrencyMetabolites
import addMetabolites
import addReactionComponentAnnotation
import addEnzymes
import parse_HMDB

from django.db import models
from api.models import *
import xml.etree.ElementTree as etree

from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)
sh = logging.StreamHandler(stream=sys.stderr)
logger.addHandler(sh)
formatter = logging.Formatter(("%(asctime)s - %(name)s - %(levelname)s - "
                               "%(message)s"))
sh.setFormatter(formatter)
logger.setLevel(logging.INFO)

annotationsToAdd = {}

db_generation_files_dir = "/project/database_generation/data/"
ressource_files_dir = "/project/related_scripts/create_the_import_files/"

'''
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
baseFolder=os.path.join(sys.path[0], "../", "database_generation", "data/")'''

def _getEnsemblArchiveURL(v):
    if v==89:
        return 'http://May2017.archive.ensembl.org/'
    elif v==82:
        return 'http://sep2015.archive.ensembl.org/'
    elif v==81:
        return 'http://jul2015.archive.ensembl.org/'
    elif v==78:
        return 'http://dec2014.archive.ensembl.org/'
    elif v==67:
        return 'http://may2012.archive.ensembl.org/'
    elif v==54:
        return 'http://may2009.archive.ensembl.org/'
    else:
        sys.exit("\n*******************************\nError:\n\tNot a known version map\n*******************************\n");

def _checkIfFileExists(files_list):
    for f in files_list:
        try:
            with open(f, 'r'):
                pass
        except IOError:
            print("Missing file ", f)
            exit(1)

# the human files and the yeast files are obviously different :)
# so wrap up all the files for the given species
def populate_human_db(database, ensembl_version, skip_first_reaction=0, skip_first_metabolite=0):
    # first check that ALL files exists
    HMRdatabase2_00_xml_file = os.path.join(ressource_files_dir, 'HMRdatabase2_00-2.xml')
    ensembl_annotation_file = os.path.join(ressource_files_dir, 'ensembl%s_hgnc_symbol_uniprotswissprot.hsapiens.tab' % ensembl_version)

    currency_mets_file = os.path.join(db_generation_files_dir, 'human_currencyMets.csv')
    mass_calculation_file = os.path.join(db_generation_files_dir, 'human_massCalc.txt')
    # HMDB_masses_file = os.path.join(db_generation_files_dir, 'hmdb_masses.csv') // now in HMDB_file
    # is hmdb_masses.csv = hmdb.tab?

    # generate using parse_HMDB.py and downloaded from http://www.hmdb.ca/system/downloads/current/hmdb_metabolites.zip (v4.0)
    HMDB_file = os.path.join(ressource_files_dir, 'HMDB.tab')
    # downloaded from ftp://ftp.ncbi.nlm.nih.gov/pubchem/Compound/Extras/ and used in using pubchem.py
    pubchem_file = os.path.join(ressource_files_dir, 'CID-Synonym-filtered')
    # downloaded from http://www.lipidmaps.org/resources/downloads/index.html and used in using lipidmaps.py


    metabolite_excel_file = os.path.join(db_generation_files_dir, 'human_metaboliteListFromExcel.txt')
    reaction_excel_file = os.path.join(db_generation_files_dir, 'human_reactionsFromExcel.txt')

    uniprot_keyword_file = os.path.join(ressource_files_dir, 'uniprot.human.keywords.tab')
    uniprot_EC_file = os.path.join(ressource_files_dir, 'uniprot.human.EC.tab')
    uniprot_function_file = os.path.join(ressource_files_dir, 'uniprot.human.function.tab')
    uniprot_catactivity_file = os.path.join(ressource_files_dir, 'uniprot.human.CatalyticActivity.tab')
    uniprot_names_file = os.path.join(ressource_files_dir, 'uniprot.human.names.tab')
    # filter only kegg reference?
    uniprot_DB_crossref_file = os.path.join(ressource_files_dir, 'uniprot.human.databasecrossreferences.tab')
    # make using grep "kegg" on 'uniprot.human.databasecrossreferences.tab
    # uniprot_DB_kegg_file = os.path.join(ressource_files_dir, 'human.kegg.tab')  # contain the NCBI gene id not kegg
    # make using  grep "GeneID" uniprot.human.databasecrossreferences.tab | sed -e 's/GeneID; \(.*\)[;]\s[-][.]/\1/g' > uniprot.ncbi.tab
    uniprot_ncbi_file = os.path.join(ressource_files_dir, 'uniprot.ncbi.tab')

    required_files = [
       HMRdatabase2_00_xml_file, ensembl_annotation_file,
       currency_mets_file, mass_calculation_file, HMDB_file,
       pubchem_file, metabolite_excel_file, reaction_excel_file,
       uniprot_keyword_file, uniprot_EC_file, uniprot_function_file,
       uniprot_catactivity_file, uniprot_names_file, uniprot_DB_crossref_file,
       uniprot_ncbi_file
    ]

    _checkIfFileExists(required_files)

    '''missingFiles = 0
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
        sys.exit("At least one missing annotation file, see above for specifications, will not attempt to add any data to the database...")'''

    ensembl_archive_url = _getEnsemblArchiveURL(ensembl_version)

    # then add the data to the database in the RIGHT order
    addSBMLData.addSBMLData(database, HMRdatabase2_00_xml_file, ensembl_version, ensembl_archive_url, skip_first_reaction=skip_first_reaction)  # addSBMLData, None is ensembl_archive_path

    logger.info("Currency Metabolites")
    addCurrencyMetabolites.addCurrencyMetabolites(database, currency_mets_file)  # addCurrencyMetabolites

    # addMetabolites
    logger.info("Add annotations for the metabolites")
    # masses = addMetabolites.readMassCalcFile(mass_calculation_file) // masses are in HMDB_file
    # hmdb = addMetabolites.readHMDBFile(HMDB_masses_file) // file missing 
    hmdb_data = parse_HMDB.parse_HMDB_tab(HMDB_file, synonyms_as_dict=True, chebi_as_dict=True, pubchem_as_dict=True)
    pubchem_db_dfile = os.path.join(ressource_files_dir, 'pubchem.db')
    if not os.path.isfile(pubchem_db_dfile):
        import pubchem
        # pubchem.generate_pubchem_db(pubchem_file)
    # lipidmaps_data = ... skip lipdsmaps data, its not use in HMR2.0
    addMetabolites.metaboliteDefinitions(database, metabolite_excel_file, hmdb_data, pubchem_db_dfile, None, skip_first_metabolite=skip_first_metabolite)

    # addReactionComponentAnnotation
    logger.info("Add 'mappings' between identifiers")
    addReactionComponentAnnotation.addReactionComponentAnnotation(database, "ensg", 0, "uniprot",
        ensembl_annotation_file, 2)
    addReactionComponentAnnotation.addReactionComponentAnnotation(database, "uniprot", 1, "up_keywords",
        uniprot_keyword_file, 2)

    # changes in the table metabolite:
    # without using pubchem database and the 'reannotate' option of metaboliteDefinitions()
    # pubchem link check and ID used, 4595 links removed
    # mass: add 2 more precision digit (not really expected)
    # all HMDB ID updated to comply with the 12 characters HMDB ID format
    # all the HMDB link have been updated using the new HMDB ID
    # 12 HMDB deleted
    # CHEBI format changed from CHEBI:12345 to 12345
    # all HMDB functions have been stored not just the last one
    # some other fields updated probably due to entries update in the v4.0 of HMDB

    # addEnzymes
    logger.info("Add annotations for the proteins")
    ec = addEnzymes.readAnnotationFile(uniprot_EC_file)
    function = addEnzymes.readAnnotationFile(uniprot_function_file)
    activity = addEnzymes.readAnnotationFile(uniprot_catactivity_file)
    ncbi = addEnzymes.readAnnotationFile(uniprot_ncbi_file)
    addEnzymes.addEnzymes(database, uniprot_names_file, ec, function, activity, ncbi, ensembl_archive_url)

    # changes in enzymes
    # kegg is now ncbi and contains only the id e.g '151112' instead of 'KEGG; hsa:151112; -.'
    # ensembl link updated to 'http://May2017 since its using the v89
    # fix fetch multiple EC and fix EC format
    # remove the last dot a the end of description
    # name have been trimed (some of them was ending with a space)

    '''
    missing db1:
    <ReactionComponent: E_3469>
    <ReactionComponent: E_78>
    <ReactionComponent: E_2741>
    <ReactionComponent: E_2790>
    missing db2:
    <ReactionComponent: E_3628>
    <ReactionComponent: E_3658>
    <ReactionComponent: E_3681>
    <ReactionComponent: E_3629>
    <ReactionComponent: E_3123>
    <ReactionComponent: E_3692>

    '''
    insert_reaction_reference(database, reaction_excel_file)

    logger.info("Then add interaction partners using: python manage.py addNumberOfInteractionPartners [database]")
    logger.info("Then add svg data using: python manage.py addCompartmentInformation database_generation/data/compartmentInfo.tab [database]")

def insert_reaction_reference(database, reaction_excel_file):
    # until Dimitra have added the annotations to the SBML file...
    with open(reaction_excel_file, 'r') as f:
        next(f) # skip the header
        for i, line in enumerate(f):
            if i != 0 and i % 1000 == 0:
                print ("Processing reaction-ref", i)
            tokens = line.strip().split("\t")
            reaction_id = tokens[0]
            if len(tokens) < 17:
                continue

            refs = tokens[16]
            refs = refs.replace('"', '')
            refs = refs.replace('*E*Re', '')
            refs = refs.replace('*P', '')
            r = [el.lstrip('PMID:').lstrip('-').strip() for el in refs.split(";") if el.strip()]
            r = [el for el in r if not re.match(r'UNIPROT|OI', el) if el]

            # fix PMID like '3071715PMID:13934211'
            fixed_pmid = []
            for el in r:
                s = el.split('PMID:')
                if len(s) > 1:
                    for i in s:
                        fixed_pmid.append(i)
                else:
                    fixed_pmid.append(el)

            if len(fixed_pmid) > len(r):
                r = fixed_pmid

            reaction = Reaction.objects.using(database).filter(id="R_"+reaction_id)
            if not reaction:
                print("No reaction found with id "+"R_"+reaction_id)
                exit(1)

            for pmid in r:
                int(el) # test all PMID string
                rr = ReactionReference.objects.using(database).filter(reaction=reaction[0], pmid=pmid)
                if not rr:
                    rr = ReactionReference(reaction=reaction[0], pmid=pmid)
                    rr.save(using=database)


def populate_yeast_db(database):
    # first check that ALL files exists

    yeast_xml_file = 'yeast76.xml'
    required_files = [yeast_xml_file]

    _checkIfFileExists(required_files)
    addSBMLData(database, yeast_xml_file, 2017, "http://yeastgenome.org/")

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('ensembl_version', type=int)
        parser.add_argument('database', type=str)
        parser.add_argument('--skip_first_reaction', type=int, default=0, action='store', dest='skip_first_reaction')
        parser.add_argument('--skip_first_metabolite', type=int, default=0, action='store', dest='skip_first_metabolite')

    def handle(self, *args, **options):
        database = options['database']
        if database == "human":
            populate_human_db(database, options['ensembl_version'], skip_first_reaction=options['skip_first_reaction'],
             skip_first_metabolite=options['skip_first_metabolite'])
        elif database == "yeast":
            populate_yeast_db(database)

