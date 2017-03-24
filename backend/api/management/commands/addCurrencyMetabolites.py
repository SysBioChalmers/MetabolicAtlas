import sys, os

from django.db import models
from api.models import ReactionComponent, Reaction

from django.core.management.base import BaseCommand

def readFile(cm_file):
    with open(cm_file, 'r') as f:
        for line in f:
            tokens = line.strip().split(",")
            component_id = "M_" + tokens[0]
            reaction_ids = ["R_" + reaction for reaction in tokens[1:]]
            component = ReactionComponent.objects.filter(id=component_id)
            if(len(component)!=1):
                sys.exit("No component found for id "+component_id)
            for reaction_id in reaction_ids:
                reaction = Reaction.objects.filter(id=reaction_id)
                if(len(reaction)!=1):
                    sys.exit("No reaction found for id "+reaction_id)
                component[0].currency_metabolites.add(reaction[0])
                #component.currency_metabolites.append(reaction)
            #db.session.add(component)
        #db.session.commit()



class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _create_tags(self):
        readFile("/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/currencyMets.csv")

    def handle(self, *args, **options):
        self._create_tags()
