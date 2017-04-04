import sys, os, csv

from django.db import models
from api.models import Enzyme, ReactionComponentAnnotation
from api.models import ReactionReactant, ModelReaction, MetabolicModel # needed in order to get the ensembl path information from the metabolic model...

from django.core.management.base import BaseCommand


#UniProtID	UniProtACC	RecommendedName	ShortName	GeneSymbol
#1433B_HUMAN	P31946	14-3-3 protein beta/alpha	KCIP-1	YWHAB
def readNameFileAndAdd(fileName, ecs, functions, activities, keggs):
    proteinsToAdd = []
    ensembl_archive_path = None
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
                if(ensembl_archive_path is None):
                    ensembl_archive_path = _getEnsemblArchivePathFromModel(rca[0].component)
                up_link = "http://www.uniprot.org/uniprot/"+uniprot_acc
                component = rca[0].component
                e_link = ensembl_archive_path+"Homo_sapiens/Gene/Summary?g="+component.long_name
                p = Enzyme(reaction_component_id=rca[0].component,
                    uniprot_acc=uniprot_acc,
                    protein_name=row[2], short_name=row[3], ec=EC, kegg=KeGG,
                    function = function, catalytic_activity=act,
                    uniprot_link = up_link, ensembl_link = e_link)
                proteinsToAdd.append(p)
            elif(len(rca)>1):
                print("More than one ReactionComponent found for uniprot "+uniprot_acc)
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

# use the reactant relationship to a reaction and then to the metabolic model via the model reaction relationship...
def _getEnsemblArchivePathFromModel(component):
    rr = ReactionReactant.objects.filter(reactant_id=component.id)
    mr = ModelReaction.objects.filter(reaction_id=rr[0].reaction_id)
    model = MetabolicModel.objects.filter(id=mr[0].model_id)
    return(model[0].ensembl_archive_path)


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'
    folder="/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/"

    def handle(self, *args, **options):
        ec = readAnnotationFile(self.folder+"uniprot.human.EC.tab")
        function = readAnnotationFile(self.folder+"uniprot.human.function.tab")
        activity = readAnnotationFile(self.folder+"uniprot.human.CatalyticActivity.tab")
        kegg = readAnnotationFile(self.folder+"human.kegg.tab")
        readNameFileAndAdd(self.folder+"uniprot.human.names.tab", ec, function, activity, kegg)
