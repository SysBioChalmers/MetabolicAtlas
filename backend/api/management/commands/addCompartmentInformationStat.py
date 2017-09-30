###########################################################
### Go through all pathways and figure out X,Y for them ###
###########################################################

import sys, os, re

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):

    def handle(self, *args, **options):
        cis = CompartmentInformation.objects.all()
        toAdd = []
        for ci in cis:
            # add the connection to the reactioncomponent
            sql1 = "SELECT * FROM reaction_component WHERE id in ("
            sql2 = "select reactant_id from reaction_reactants where reaction_id in ("
            sql3 = "select reaction_id from subsystem_reaction where subsystem_id in ("
            sql4 = "select subsystem_id from tile_subsystems where compartmentinformation_id="
            sql= sql1 + sql2 + sql3 + sql4 + str(ci.id)+")))"
            rcs = ReactionComponent.objects.raw(sql)
            nr_metabolites = 0
            for rc in rcs:
                rccis = ReactionComponentCompartmentInformation.objects.filter(component=rc, compartmentinfo=ci)
                if(len(rccis)<1):
                    add = ReactionComponentCompartmentInformation(component=rc, compartmentinfo=ci)
                    add.save()
                nr_metabolites = nr_metabolites + 1

            # add the connection to the reactions
            sql5 = "SELECT * FROM reaction WHERE id in ("
            sql = sql5 + sql3 + sql4 + str(ci.id)+"))"
            rs = Reaction.objects.raw(sql)
            for r in rs:
                rcis = ReactionCompartmentInformation.objects.filter(reaction=r, compartmentinfo=ci)
                if(len(rcis)<1):
                    add = ReactionCompartmentInformation(reaction=r, compartmentinfo=ci)
                    add.save()
            nr_reactions = len(list(rs))

            # how many subsystems?
            sql6 = "SELECT * from subsystems WHERE id in ("
            sql = sql6 + sql4 + str(ci.id)+")"
            s = Subsystem.objects.raw(sql)
            nr_subsystems = len(list(s))

            # how many enzymes?
            sql7 = sql1 + "select modifier_id from reaction_modifiers where reaction_id in ("
            sql7 = sql7 + sql3 + sql4 + str(ci.id)+")))"
            rcs = ReactionComponent.objects.raw(sql7)
            nr_enzymes = 0
            for rc in rcs:
                rccis = ReactionComponentCompartmentInformation.objects.filter(component=rc, compartmentinfo=ci)
                if(len(rccis)<1):
                    add = ReactionComponentCompartmentInformation(component=rc, compartmentinfo=ci)
                    add.save()
                nr_enzymes = nr_enzymes + 1

            # finally update the object
            CompartmentInformation.objects.filter(id=ci.id).update(nr_reactions=nr_reactions, nr_subsystems=nr_subsystems, nr_metabolites=nr_metabolites, nr_enzymes=nr_enzymes)
