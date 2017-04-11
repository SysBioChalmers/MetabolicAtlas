import sys, os

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand

def getFirstOrderInteractionPartners(reaction_component):
    # first get all reactions that the reaction component participates in
    as_reactant = [MetaboliteReaction(rc, 'reactant') for rc in reaction_component.reactions_as_reactant.all()]
    as_product = [MetaboliteReaction(rc, 'product') for rc in reaction_component.reactions_as_product.all()]
    as_modifier = [MetaboliteReaction(rc, 'modifier') for rc in reaction_component.reactions_as_modifier.all()]
    reactions = as_reactant + as_product + as_modifier
    # then get all the unique reaction components for these reactions
    unique_reaction_components = {}
    for r in reactions:
        unique_reaction_components[r.reaction_id] = "";
    return(len(unique_reaction_components))


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def handle(self, *args, **options):
        """ Calculate the number of interaction partners for each ReactionComponent id """
        nrsToAdd = []
        components = ReactionComponent.objects.all()
        for component in components:
            # get the 1st order interaction partners @TODO would be nice if the "same" code as the connected_metabolites view
            first = getFirstOrderInteractionPartners(component)
            nrReactions = len(ReactionModifier.objects.filter(modifier_id=component.id))
            nr = NumberOfInteractionPartners(reaction_component_id = component,
                first_order = first, second_order = None, third_order = None,
                catalysed_reactions = nrReactions)
            nrsToAdd.append(nr)
        NumberOfInteractionPartners.objects.bulk_create(nrsToAdd)
