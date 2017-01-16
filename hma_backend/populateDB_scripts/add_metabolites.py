import sys

from hma_backend import db
from hma_backend.models import *
from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

verbose = False

def main(fileName):
    notFoundCount = 0
    with open(annFile, 'r') as f:
        for line in f:
            print("Line is "+line)
            columns = line.strip().split("\t")
            # the ensembl download annotation files will contain an ENSG id without the actual annotation column...
            if len(tokens) > annCol:
                annotation = tokens[annCol]
                if(idType == "ensg"):
                    enzymeId = tokens[idCol]
                    try:
                        component = ReactionComponent.query.filter(
                            and_(ReactionComponent.component_type == "enzyme",
                                ReactionComponent.long_name == enzymeId)).one()
                        _addAnnotation(db, component.id, annType, annotation)
                    except NoResultFound:
                        if verbose:
                            print("No enzyme found for ensg "+enzymeId)
                elif(idType == "uniprot"):
                    upId = tokens[idCol]
                    #print("Looking at uniprot id "+upId+" for line "+line)
                    try:
                        up = ReactionComponentAnnotation.query.filter(
                            and_(ReactionComponentAnnotation.annotation_type=='uniprot',
                                ReactionComponentAnnotation.annotation == upId)).one()
                        _addAnnotation(db, up.component_id, annType, annotation)
                        prevUp = upId
                    except NoResultFound:
                        if verbose:
                            print("No ann found for "+upId)
                    except MultipleResultsFound:
                        ups = ReactionComponentAnnotation.query.filter(
                            and_(ReactionComponentAnnotation.annotation_type=='uniprot',
                                ReactionComponentAnnotation.annotation == upId)).all()
                        for up in ups:
                            _addAnnotation(db, up.component_id, annType, annotation)
                        prevUp = None
                elif(idType == "metName"):
                    name = tokens[idCol]
                    try:
                        met = ReactionComponent.query.filter(
                            ReactionComponent.long_name == name).one()
                        _addAnnotation(db, met.id, annType, annotation)
                    except NoResultFound:
                        print("No reaction comopnent found for metabolite name '"+name+"' ")
                        notFoundCount = notFoundCount + 1
                    except MultipleResultsFound:
                        print("Multiple rc found for "+name)
        db.session.commit()
        if(idType == "metName" and notFoundCount>0):
            print("ERROR! there were HMR metabolite names that were not found in DB, fix these before proceding!")

def _addAnnotation(db, cId, t, ann):
    # make the annotation
    ann = ReactionComponentAnnotation(
        component_id = cId, annotation_type = t, annotation = ann)
    db.session.add(ann)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(("Usage: python add_metabolites.py <filename>"))
        sys.exit(1)
    main(sys.argv[1])
