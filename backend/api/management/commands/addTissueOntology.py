import sys, os, csv

from django.db import models
from api.models import TissueOntology

from django.core.management.base import BaseCommand

def addTissueOntology(bto_file):
    """ Read the BRENDA Tissue Ontology from file """
    toToAdd = []
    with open(bto_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(f) # skip header
        for bto in reader:
            ontology = TissueOntology(id=bto[0], name=bto[1], definition=bto[2])
            toToAdd.append(ontology)
    TissueOntology.objects.bulk_create(toToAdd)

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'
    folder="/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/"
    bto_file=folder+"BTO.tab"

    def handle(self, *args, **options):
        addTissueOntology(self.bto_file)
