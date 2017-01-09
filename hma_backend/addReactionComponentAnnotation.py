import sys

from hma_backend import db
from hma_backend.models import *
from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound

verbose = False

def main(idType, idCol, annType, annFile, annCol):
    with open(annFile, 'r') as f:
        for line in f:
            tokens = line.strip().split("\t")
            # the ensembl download annotation files will contain an ENSG id without the actual annotation column...
            if len(tokens) > annCol:
                annotation = tokens[annCol]
                if(idType == "ensg"):
                    enzymeId = tokens[idCol]
                    try:
                        component = ReactionComponent.query.filter(
                            and_(ReactionComponent.component_type == "enzyme",
                                ReactionComponent.long_name == enzymeId)).one()
                        # make the annotation
                        ann = ReactionComponentAnnotation(
                            component_id = component.id,
                            annotation_type=annType,
                            annotation=annotation)
                        db.session.add(ann)
                        if verbose:
                            print("Adding "+annotation+" for "+enzymeId+" with rcid "+component.id)
                    except NoResultFound:
                        if verbose:
                            print("No enzyme found for ensg "+enzymeId)
        db.session.commit()


if __name__ == "__main__":
    print("length")
    print(len(sys.argv))
    print(sys.argv[1])
    if len(sys.argv) != 6:
        print(("Usage: python addReactionComponentAnnotation.py "
               "<id_type> <id_col> <annotation_type> <annotation_file> <ann_col>\n"
               "for example ensg 0 swissprotAcc ... 1"))
        sys.exit(1)
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], int(sys.argv[5]))
