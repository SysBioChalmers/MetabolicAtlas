############################################################
# TODO is a work in progress, do not work                  #
############################################################
import sys, os

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand

def getFirstOrderInteractionPartners(reaction_component):
    # first get all reactions that the reaction component participates in
    as_reactant = [r for r in reaction_component.reactions_as_reactant.all(). \
    prefetch_related('reactants', 'products', 'modifiers', 'reactants__enzyme', 'reactants__metabolite', \
            'products__enzyme', 'products__metabolite', 'modifiers__enzyme', 'modifiers__metabolite', \
            'reactants__compartment', 'products__compartment', 'modifiers__compartment')
    ]
    as_product = [r for r in reaction_component.reactions_as_product.all(). \
    prefetch_related('reactants', 'products', 'modifiers', 'reactants__enzyme', 'reactants__metabolite', \
            'products__enzyme', 'products__metabolite', 'modifiers__enzyme', 'modifiers__metabolite', \
            'reactants__compartment', 'products__compartment', 'modifiers__compartment')
    ]
    as_modifier = [r for r in reaction_component.reactions_as_modifier.all(). \
    prefetch_related('reactants', 'products', 'modifiers', 'reactants__enzyme', 'reactants__metabolite', \
            'products__enzyme', 'products__metabolite', 'modifiers__enzyme', 'modifiers__metabolite', \
            'reactants__compartment', 'products__compartment', 'modifiers__compartment')
    ]
    reactions = as_reactant + as_product + as_modifier
    # then get all the unique reaction components for these reactions
    unique_reaction_components = {}
    for r in reactions:
        print (r.reaction_id)
        exit()
        unique_reaction_components[r.reaction_id] = None;
    return len(unique_reaction_components)


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def add_arguments(self, parser):
        import argparse
        parser.add_argument('database', type=str)

    def handle(self, *args, **options):
        database = options['database']
        """ Calculate the number of interaction partners for each ReactionComponent id """
        nrsToAdd = []
        components = ReactionComponent.objects.using(database).all()
        for i, component in enumerate(components):
            if i != 0 and i % 1000 == 0:
                print ("Processing component", i)
            # get the 1st order interaction partners @TODO would be nice if the "same" code as the connected_metabolites view
            first = getFirstOrderInteractionPartners(component)
            nrReactions = len(ReactionModifier.objects.using(database).filter(modifier_id=component.id))
            nr = NumberOfInteractionPartners.objects.using(database).filter(reaction_component_id=component)
            if not nr:
                nr = NumberOfInteractionPartners(reaction_component_id = component,
                    first_order = first, second_order = None, third_order = None,
                    catalysed_reactions = nrReactions)
                nr.save(using=database)
