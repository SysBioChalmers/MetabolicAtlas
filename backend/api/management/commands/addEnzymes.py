import sys, os, csv

from django.db import models
from api.models import Enzyme, ReactionComponentAnnotation

from django.core.management.base import BaseCommand

#UniProtID	UniProtACC	RecommendedName	ShortName	GeneSymbol
#1433B_HUMAN	P31946	14-3-3 protein beta/alpha	KCIP-1	YWHAB
def readNameFileAndAdd(fileName, ecs, functions, activities, keggs):
    proteinsToAdd = []
    with open(fileName, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        next(f) # skip the header
        for row in reader:
            uniprot_acc = row[1]
            rca = ReactionComponentAnnotation.objects.filter(annotation=uniprot_acc)
            if(len(rca)==1):
                EC = None; KeGG = None; function = None; act = None
                if(uniprot_acc in ecs):
                    EC = ecs[uniprot_acc]
                if(uniprot_acc in functions):
                    function = functions[uniprot_acc]
                if(uniprot_acc in activities):
                    act = activities[uniprot_acc]
                if(uniprot_acc in keggs):
                    KeGG = keggs[uniprot_acc]
                p = Enzyme(reaction_component_id=rca[0].reaction_component_id,
                    uniprot_acc=uniprot_acc,
                    protein_name=row[2], short_name=row[3], ec=EC, kegg=KeGG,
                    function = function, catalytic_activity=act)
                proteinsToAdd.append(p)
    Enzyme.objects.bulk_create(proteinsToAdd)


# please remember that the uniprot id is the first column so the uniprot accession is the second :)
def readAnnotationFile(fileName):
    annotations = {}
    with open(fileName, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        next(f) # skip the header
        for row in reader:
            if(len(row)<2):
                print("not found enough data in line "+row[0])
            annotations[row[1]] = row[2]
    return(annotations)


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'
    folder="/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/"

    def _create_tags(self):
        ec = readAnnotationFile(self.folder+"uniprot.human.EC.tab")
        function = readAnnotationFile(self.folder+"uniprot.human.function.tab")
        activity = readAnnotationFile(self.folder+"uniprot.human.CatalyticActivity.tab")
        kegg = readAnnotationFile(self.folder+"human.kegg.tab")
        readNameFileAndAdd(self.folder+"uniprot.human.names.tab", ec, function, activity, kegg)


    def handle(self, *args, **options):
        self._create_tags()
