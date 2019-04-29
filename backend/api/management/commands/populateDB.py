import sys, os

# add db generation files to path
sys.path.insert(0, "/project/database_generation/")
import addYAMLData
from django.db import models
from api.models import *
from django.conf import settings

from django.core.management.base import BaseCommand

def populate_database(database, yaml_file, overwrite=False, metadata_only=False, content_only=False):

    # check if the database exist
    if database not in settings.DATABASES:
        print("Error: database '%s' is not in the settings file" % database)
        return

    addYAMLData.load_YAML(database, yaml_file, overwrite=overwrite, metadata_only=metadata_only, content_only=content_only)

    print("""
        Then add annoations with:

            python manage.py addAnnotations %s [type|'test'|'all'] [annotation_file]

        Add svg data with:

            python manage.py addMapsInformation %s ['compartment'|'subsystem'] [SVG file directory] database_generation/%s/[metadatafile].tsv

        Add currency met with:

            python manage.py addCurrencyMetabolites %s

        Add interaction partners info with:

            python manage.py addNumberOfInteractionPartners %s

        if applicable, Add HPA tissue/enzyme RNA levels with:

            python manage.py addHPAexpression %s

        """ % (database, database, database, database, database, database))


class Command(BaseCommand):

    def add_arguments(self, parser):
        #  python manage.py populateDB hmr2 database_generation/human1/model.yml
        parser.add_argument('database', type=str)
        parser.add_argument('yaml file', type=str)
        parser.add_argument('--overwrite', action='store_true', dest='overwrite', default=False)
        parser.add_argument('--metadata-only', action='store_true', dest='metadata_only')
        parser.add_argument('--content-only', action='store_true', dest='content_only')

    def handle(self, *args, **options):
        populate_database(options['database'], options['yaml file'], overwrite=options['overwrite'], metadata_only=options['metadata_only'], content_only=options['content_only'])


