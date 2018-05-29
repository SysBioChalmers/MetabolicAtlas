import sys, os

# add db generation files to path
sys.path.insert(0, "/project/database_generation/")
import addYAMLData
from django.db import models
from api.models import *

from django.core.management.base import BaseCommand

def insert_model_metadata(database, yaml_file, model_label, model_pmid):

    """
        design for yml metadata
        "metadata": {
            "id": {"type": "string"}, e.g. HMR3
            "label": {"type": "string"}, e.g. HMR 3.0
            "full_name": {"type": "string"}, e.g. Human Metabolic Reaction version 3
            "description": {"type": "string"}, 
            "version": {
                "type": "integer",
                "default": 1,
            },
            "authors": [
                {
                    first_name: {"type": "string"},
                    last_name: {"type": "string"},
                    email: {"type": "string"},
                    organization: {"type": "string"},
                },
            ]
        }
    """

    # get the id, name, label, authors from the yaml here

    try:
        gem = GEModel.objects.using('gems').get(label=model_label)
    except GEModel.DoesNotExist:
        print ("Error: cannot find model in gems database, using label '%s'" % model_label)
        exit(1)

    model = GEM.objects.using('gems').filter(name=gem.gemodelset.name, short_name=gem.label, database_name=database)
    if not model:
        try:
            publication = GEModelReference.objects.using('gems').get(pubmed=model_pmid) # 24419221 for hmr2
            model = GEM(name=gem.gemodelset.name, short_name=gem.label, database_name=database, model=gem, publication=publication)
        except GEModelReference.DoesNotExist:
            model = GEM(name=gem.gemodelset.name, short_name=gem.label, database_name=database, model=gem)
        model.save(using='gems')
    else:
        model= model[0]

    temp_author = {
        'first_name': 'Adil',
        'last_name': 'Mardinoglu',
        'email': 'adilm@chalmers.se',
        'organization': 'Chalmers University of Technology, Gothenburg',
    }

    a = Author.objects.using('gems').filter(given_name=temp_author['first_name'],
                    family_name=temp_author['last_name'],
                    email=temp_author['email'],
                    organization=temp_author['organization'])
    if not a:
        author = Author(given_name=temp_author['first_name'],
                    family_name=temp_author['last_name'],
                    email=temp_author['email'],
                    organization=temp_author['organization'])
        author.save(using='gems')

        ma = GEMAuthor(model=model, author=author)
        ma.save(using='gems')


def populate_database(database, yaml_file, model_label, model_pmid, delete=False):

    # Instert the model in the 
    insert_model_metadata(database, yaml_file, model_label, model_pmid)
    addYAMLData.load_YAML(database, yaml_file, delete=delete)

    print("""
         Then add annoations with:

            python manage.py addAnnotations %s [type|'test'|'all'] [annotation_file]

        Add svg data with:

            python manage.py addCompartmentSubsystemInformation %s --compartment-svg-file database_generation/%s/compartmentSVF.tsv --write-connectivity-files

        Add currency met with:

            python manage.py addCurrencyMetabolites %s

        Add interaction partners with:

            python manage.py addNumberOfInteractionPartners %s

        """ % (database, database, database, database, database))


class Command(BaseCommand):

    def add_arguments(self, parser):
        #  python manage.py populateDB hmr2 database_generation/hmr2/model.yml "HMR 2.0" 24419221
        parser.add_argument('database', type=str)
        parser.add_argument('yaml file', type=str)
        parser.add_argument('model label', type=str)
        parser.add_argument('model pmid', type=str)
        parser.add_argument('--delete', action='store_true', dest='delete')

    def handle(self, *args, **options):
        populate_database(options['database'], options['yaml file'],  options['model label'], options['model pmid'], delete=options['delete'])


