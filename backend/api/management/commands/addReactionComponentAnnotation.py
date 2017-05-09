import sys, os, csv

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand
annotationsToAdd = {}
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
                        _addAnnotation(rca[0].component, annType, annotation)
                    else:
                        for up in rca:
                            _addAnnotation(up.component, annType, annotation)
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
        temp = []
        for a in annotationsToAdd:
            temp.append(annotationsToAdd[a])
        ReactionComponentAnnotation.objects.bulk_create(temp)
        print("Added "+str(len(temp))+" reaction component annotations of type "+annType)
        if(idType == "metName" and notFoundCount>0):
            print("ERROR! there were HMR metabolite names that were not found in DB, fix these before proceding!")


def _addAnnotation(c, t, ann):
    # make the annotation
    ann = ReactionComponentAnnotation(
        component = c, annotation_type = t, annotation = ann)
    annotationsToAdd[str(ann)] = ann # ensure only unique annotations are added!


class Command(BaseCommand):
    help = 'our help string comes here'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help="the path to the file to read")
        parser.add_argument('id_type', type=str, help="(ensg|uniprot)")
        parser.add_argument('id_col', type=int, help="the colNr of the identifier")
        parser.add_argument('annotation_type', type=str, help="(uniprot|up_keywords)")
        parser.add_argument('annotation_col', type=str, help="(the colNr of the annotation")

    def handle(self, *args, **options):
        readFileAndAdd(str(options['id_type']), int(options['id_col']),
            str(options['annotation_type']), str(options['file']),
            int(options['annotation_col']))
