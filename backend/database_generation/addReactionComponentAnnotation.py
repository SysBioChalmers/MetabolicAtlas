##########################################################################
# the actual code to read and import annotations for reaction components #
##########################################################################

def addReactionComponentAnnotation(idType, idCol, annType, annFile, annCol):
    notFoundCount = 0
    annotationsToAdd = {}
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
                        ann = ReactionComponentAnnotation(
                            component = component[0], annotation_type = annType, annotation = annotation)
                        annotationsToAdd[str(ann)] = ann # ensure only unique annotations are added!
                elif(idType == "uniprot"):
                    upId = tokens[idCol]
                    rca = ReactionComponentAnnotation.objects.filter(
                        annotation_type='uniprot').filter(annotation=upId)
                    if(len(rca)<1):
                        if verbose:
                            print("No ann found for "+upId)
                    elif(len(rca)==1):
                        ann = ReactionComponentAnnotation(
                            component = rca[0].component, annotation_type = annType, annotation = annotation)
                        annotationsToAdd[str(ann)] = ann # ensure only unique annotations are added!
                    else:
                        for up in rca:
                            ann = ReactionComponentAnnotation(
                                component = up.component, annotation_type = annType, annotation = annotation)
                            annotationsToAdd[str(ann)] = ann # ensure only unique annotations are added!
                elif(idType == "metName"):
                    name = tokens[idCol]
                    met = ReactionComponent.objects.filter(long_name=name)
                    if(len(met)<1):
                        print("No reaction comopnent found for metabolite name '"+name+"' ")
                        notFoundCount = notFoundCount + 1
                    elif(len(met)==1):
                        ann = ReactionComponentAnnotation(
                            component = met[0], annotation_type = annType, annotation = annotation)
                        annotationsToAdd[str(ann)] = ann # ensure only unique annotations are added!
                    else:
                        print("Multiple rc found for "+name)
        temp = []
        for a in annotationsToAdd:
            temp.append(annotationsToAdd[a])
        ReactionComponentAnnotation.objects.bulk_create(temp)
        print("Added "+str(len(temp))+" reaction component annotations of type "+annType)
        if(idType == "metName" and notFoundCount>0):
            print("ERROR! there were HMR metabolite names that were not found in DB, fix these before proceding!")
