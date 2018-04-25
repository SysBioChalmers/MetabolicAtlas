####################################################################
# the actual code to read and import enzymes and their annotations #
####################################################################

from api.models import *
import csv

#UniProtID	UniProtACC	RecommendedName	ShortName	GeneSymbol
#1433B_HUMAN	P31946	14-3-3 protein beta/alpha	KCIP-1	YWHAB
def addEnzymes(database, fileName, ecs, functions, activities, ncbi_dict, ensembl_archive_url):
    # proteinsToAdd = []
    proteinsAdded = {}

    if not ensembl_archive_url:
        print ("Error: you must provide a ensembl archive url")
        exit(1)

    with open(fileName, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        next(f) # skip the header
        for i, row in enumerate(reader):
            if i != 0 and i % 1000 == 0:
                print ("Processing enzyme", i)
            uniprot_acc = row[1].strip()
            # TODO do not ReactionComponentAnnotation?
            proteinsMatched = ReactionComponentAnnotation.objects.using(database). \
                select_related('component').filter(annotation=uniprot_acc)
            for rca in proteinsMatched:
                if rca.component in proteinsAdded:
                    continue

                EC = None; ncbi = None; function = None; act = None
                if uniprot_acc in ecs:
                    EC = ecs[uniprot_acc].rstrip(';')
                if uniprot_acc in functions:
                    function = functions[uniprot_acc]
                if uniprot_acc in activities:
                    act = activities[uniprot_acc]
                if uniprot_acc in ncbi_dict:
                    ncbi = ncbi_dict[uniprot_acc]

                up_link = "http://www.uniprot.org/uniprot/%s" % uniprot_acc
                component = rca.component
                e_link = "%sHomo_sapiens/Gene/Summary?g=%s" % (ensembl_archive_url, component.long_name)
                p = Enzyme.objects.using(database).filter(reaction_component=rca.component)
                if not p:
                    p = Enzyme(reaction_component=rca.component,
                        uniprot_acc=uniprot_acc,
                        protein_name=row[2].strip(), short_name=row[3].strip(), ec=EC, ncbi=ncbi,
                        function=function, catalytic_activity=act, ensembl_link=e_link)
                    p.save(using=database)
                proteinsAdded[rca.component] = None


# please remember that the uniprot id is the first column so the uniprot accession is the second :)
def readAnnotationFile(fileName):
    annotations = {}
    with open(fileName, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        next(f) # skip the header
        for row in reader:
            if len(row) < 2:
                print("not found enough data in line", row[0])
                exit(1)
            annotations[row[1].strip()] = row[2].strip()
    return annotations

# use the reactant relationship to a reaction and then to the metabolic model via the model reaction relationship...
def _getEnsemblArchivePathFromModel(component):
    reaction = ReactionModifier.objects.using(database).filter(modifier_id=component.id)
    mr = GEMReaction.objects.using(database).filter(reaction_id=reaction[0].reaction_id)
    model = GEM.objects.using(database).filter(id=mr[0].model_id)
    return(model[0].ensembl_archive_path)
