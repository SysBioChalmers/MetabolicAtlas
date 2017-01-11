import sys, os, csv, re

sys.path.append(os.path.join(sys.path[0],"../"))

from hma_backend import db
from hma_backend.models import *
from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

verbose = False


def main(proteinsFileName, keggFileName, ecFileName, functionFileName):
    keggInfo = readKEGG(keggFileName)
    ecInfo = readEC(ecFileName)
    functions = readFunction(functionFileName)
    with open(proteinsFileName, 'r') as f:
        next(f) # skip the headerline!
        for line in f:
            # set the extra annotations to 'null'
            short_name = None; ec = None; kegg = None; function = None;
            #print("Line is "+line)
            columns = line.strip().split("\t")
            uniprotAcc = columns[1]
            long_name = columns[2]
            if(len(columns)>3):
                short_name = columns[3]
            if uniprotAcc in ecInfo:
                ec = ecInfo[uniprotAcc]
            if uniprotAcc in keggInfo:
                kegg = keggInfo[uniprotAcc]
            if uniprotAcc in functions:
                function = functions[uniprotAcc]
            enzyme = Enzyme(
                protein_name = long_name,
                short_name = short_name,
                ec = ec,
                kegg = kegg,
                function = function
            )
            try:
                ups = ReactionComponentAnnotation.query.filter(
                    and_(ReactionComponentAnnotation.annotation_type == 'uniprot',
                        ReactionComponentAnnotation.annotation == uniprotAcc)).all()
                for up in ups:
                    component = ReactionComponent.query.filter(
                        ReactionComponent.id == up.component_id).one()
                    enzyme.components.append(component)
                db.session.add(enzyme) # only add the enzymes that are found in HMR!
            except NoResultFound:
                # do nothing here as most of the proteins in uniprot are not part of the HMR
                if verbose:
                    print("skippping "+uniprotAcc)
        db.session.commit()

def readKEGG(filename):
    with open(filename, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        keggs = {}
        for row in reader:
            uniprotAcc = row[1]
            KEGG = re.sub(r"; -.", "", re.sub(r"KEGG; ", "", row[2])).strip()
            if( uniprotAcc in keggs):
                keggs[uniprotAcc] = keggs[uniprotAcc] + " ; " + KEGG
            else:
                keggs[uniprotAcc] = KEGG
    return keggs

def readEC(filename):
    with open(filename, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        ecs = {}
        for row in reader:
            uniprotAcc = row[1]
            EC = re.sub(r";", "", row[2]).strip()
            if( uniprotAcc in ecs):
                ecs[uniprotAcc] = ecs[uniprotAcc] + " ; " + EC
            else:
                ecs[uniprotAcc] = EC
    return ecs

def readFunction(filename):
    with open(filename, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        functions = {}
        for row in reader:
            uniprotAcc = row[1]
            function = row[2]
            functions[uniprotAcc] = function
    return functions


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(("Usage: python add_metabolites.py <proteinnames> <keggfilename> <ecfilename> <functionfilename>"))
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
