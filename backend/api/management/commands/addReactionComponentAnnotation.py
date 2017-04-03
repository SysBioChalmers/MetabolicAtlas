import sys, os, csv

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand
annotationsToAdd = []
verbose = False

def readFileAndAdd(idType, idCol, annType, annFile, annCol):
    notFoundCount = 0
    with open(annFile, 'r') as f:
        for line in f:
            tokens = line.strip().split("\t")
            # the ensembl download annotation files will contain an ENSG id without the actual annotation column... (eg when its missing!)
            if len(tokens) > annCol:
                annotation = tokens[annCol]
                if(idType == "ensg"):
                    enzymeId = tokens[idCol]
                    component = ReactionComponent.objects.filter(
                        component_type = "enzyme").filter(
                            long_name = enzymeId)
                    if(len(component)<1):
                        if verbose:
                            print("No enzyme found for ensg "+enzymeId)
                    else:
                        _addAnnotation(component[0], annType, annotation)
                elif(idType == "uniprot"):
                    upId = tokens[idCol]
                    rca = ReactionComponentAnnotation.objects.filter(
                        annotation_type='uniprot').filter(annotation=upId)
                    if(len(rca)<1):
                        if verbose:
                            print("No ann found for "+upId)
                    elif(len(rca)==1):
                        _addAnnotation(rca[0].reaction_component_id, annType, annotation)
                    else:
                        for up in rca:
                            _addAnnotation(up.reaction_component_id, annType, annotation)
                elif(idType == "metName"):
                    name = tokens[idCol]
                    met = ReactionComponent.objects.filter(long_name=name)
                    if(len(met)<1):
                        print("No reaction comopnent found for metabolite name '"+name+"' ")
                        notFoundCount = notFoundCount + 1
                    elif(len(met)==1):
                        _addAnnotation(met[0], annType, annotation)
                    else:
                        print("Multiple rc found for "+name)
        ReactionComponentAnnotation.objects.bulk_create(annotationsToAdd)
        if(idType == "metName" and notFoundCount>0):
            print("ERROR! there were HMR metabolite names that were not found in DB, fix these before proceding!")

def _addAnnotation(c, t, ann):
    # make the annotation
    ann = ReactionComponentAnnotation(
        reaction_component_id = c, annotation_type = t, annotation = ann)
    annotationsToAdd.append(ann)



class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'
    folder="/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/"

    def handle(self, *args, **options):
        readFileAndAdd("ensg", 0, "uniprot", self.folder+"ensembl82_uniprot_swissprot.tab", 1)
        readFileAndAdd("uniprot", 1, "up_keywords", self.folder+"uniprot.human.keywords.tab", 2) # about an hour!
