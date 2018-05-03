##########################################################################
# the actual code to read and import annotations for reaction components #
##########################################################################

from api.models import *

# TODO can we not use this table?
def addReactionComponentAnnotation(database, idType, idCol, annType, annFile, annCol):
    notFoundCount = 0
    annotationsToAdd = {}
    verbose = False
    with open(annFile, 'r') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            if i % 1000 == 0:
                print ("Processing annotation", i)

            tokens = line.strip().split("\t")
            if not tokens:
                continue
            # the ensembl download annotation files will contain an ENSG id without the actual annotation column... (eg when its missing!)
            if len(tokens) > annCol: # ????
                annotation = tokens[annCol] # ????
                if idType == "ensg":
                    enzymeId = tokens[idCol]
                    component = ReactionComponent.objects.using(database).filter(
                        component_type="enzyme").filter(
                            long_name=enzymeId)
                    if not component:
                        if verbose:
                            print("No enzyme found for ensg "+enzymeId)
                    else:
                        ann = ReactionComponentAnnotation(
                            component=component[0], annotation_type=annType, annotation=annotation)
                        annotationsToAdd[str(ann)] = ann # ensure only unique annotations are added!
                elif idType == "uniprot":
                    upId = tokens[idCol]
                    # print ("idType", idType, "annType", annType, "upId", upId, "annotation", annotation)
                    # print (line)
                    rca = ReactionComponentAnnotation.objects.using(database).select_related('component').filter(
                        annotation_type='uniprot').filter(annotation=upId)
                    if not rca:
                        if verbose:
                            print("No ann found for "+upId)
                    elif len(rca) == 1:
                        ann = ReactionComponentAnnotation(
                            component=rca[0].component, annotation_type=annType, annotation=annotation)
                        annotationsToAdd[str(ann)] = ann # ensure only unique annotations are added!
                    else:
                        for up in rca:
                            ann = ReactionComponentAnnotation(
                                component=up.component, annotation_type=annType, annotation=annotation)
                            annotationsToAdd[str(ann)] = ann # ensure only unique annotations are added!
                    #exit(1)
                elif idType == "metName":
                    name = tokens[idCol]
                    met = ReactionComponent.objects.using(database).filter(long_name=name)
                    if not met:
                        print("No reaction component found for metabolite name '%s' " % name)
                        notFoundCount += 1
                    elif len(met) == 1:
                        ann = ReactionComponentAnnotation(
                            component=met[0], annotation_type=annType, annotation=annotation)
                        annotationsToAdd[str(ann)] = ann # ensure only unique annotations are added!
                    else:
                        print("Multiple rc found for "+name)
        # temp = []
        print ("saving annotations...")
        for a in annotationsToAdd:
            # temp.append(annotationsToAdd[a])
            annotationsToAdd[a].save(using=database)
        # ReactionComponentAnnotation.objects.bulk_create(temp)
        print("Added %s reaction component annotations of type " % len(annotationsToAdd), annType)
        if idType == "metName" and notFoundCount:
            print("ERROR! there were HMR metabolite names that were not found in DB, fix these before proceding!")
