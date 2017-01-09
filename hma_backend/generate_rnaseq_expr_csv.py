"""Convert HPA rnaseq expression data to CSV.

The output CSV files are formatted for importing hma_backend
ExpressionData into PostgreSQL.
"""

from multiprocessing import Process, Queue, cpu_count
from statistics import median
import csv
import logging
import re
import sys

from hma_backend.models import ReactionComponent


#NUM_CPUS = cpu_count()
NUM_CPUS=1

logger = logging.getLogger(__name__)
sh = logging.StreamHandler(stream=sys.stderr)
logger.addHandler(sh)
formatter = logging.Formatter(("%(asctime)s - %(name)s - %(levelname)s - "
                               "%(message)s"))
sh.setFormatter(formatter)
logger.setLevel(logging.INFO)


def get_rnaseq_expressions(gene_ids, rnaseq_expr_file, btoMap):
    """Read rnaseq expressions from supplied file."""
    logger.info("Reading rnaseq file...")
    q = Queue()
    queue_proc = Process(target=queue_rnaseq_expressions,
                         args=(q, rnaseq_expr_file, NUM_CPUS, btoMap))
    queue_proc.start()
    workers = []
    for i in range(NUM_CPUS):
        worker = Process(target=save_rnaseq_expressions, args=(i, q, gene_ids))
        worker.start()
        workers.append(worker)
    logger.info("Reading rnaseq file...done!")


def queue_rnaseq_expressions(q, rnaseq_expr_file, num_workers, btoMap):
    """Read expressions from file and publish to a queue."""
    logger.info("Publish expressions")
    for expressions in read_rnaseq_expressions(rnaseq_expr_file, btoMap):
        q.put(expressions)
    logger.info("Publisher done, notifying workers...")
    for i in range(num_workers):
        q.put("DONE!")
    logger.info("Workers notified")


# we are currently including all expression levels from 'all' individuals
# and then taking the median...
def read_rnaseq_expressions(filename, btoMap):
    """Read expressions from file."""
    tissues = get_tissues(read_headers(filename))
    with open(filename, "r") as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            expressions = []
            for tissue in tissues:
                levels = get_levels(tissue, row)
                gene_id = row['ensgid']
                expression = {}
                expression['gene_id'] = gene_id
                expression['transcript_id'] = row['enstid']
                tissue = re.sub(" \d$", "", tissue) # if it ends with a number like stomach 1
                if(tissue not in btoMap):
                    sys.exit("Missing bto id for tissue "+tissue+" in file"+sys.argv[3])
                expression['tissue'] = tissue
                expression['bto'] = btoMap[tissue]
                # FIXME what cell_type should we use here?
                expression['cell_type'] = "N/A"
                expression['level'] = median(levels)
                # FIXME don't hardcode fields
                expression['expression_type'] = "rnaseq"
                expression['source'] = "HMA V14"
                expressions.append(expression)
            yield expressions


def read_headers(filename):
    """Read headers from TSV file."""
    with open(filename, "r") as f:
        line = next(f)
        headers = line.split("\t")
    return [header.strip() for header in headers]


def get_tissues(headers):
    """Get tissue names from headers."""
    tissues = set()
    for header in headers:
        match = re.search("^(.*)\.V\d+$", header)
        if match:
            tissues.add(match.group(1))
    return sorted(list(tissues))


def get_levels(tissue, row):
    """Get tissue levels for supplied row."""
    levels = []
    for key in row.keys():
        pattern = "^{0}\.V\d+$".format(tissue)
        match = re.search(pattern, key)
        if match:
            if row[key] == "NA":
                # FIXME treat as 0 or skip?
                levels.append(0)
            else:
                levels.append(float(row[key]))
    return levels

def readBTO(filename):
    with open(filename, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        bto = {}
        for row in reader:
            bto[row[0]] = row[1]
    return bto


def save_rnaseq_expressions(worker_id, q, gene_ids):
    """Read expressions from queue and save to CSV file.

    The output file is used to import data into PostgreSQL.
    """
    logger.info("Worker {0} started!".format(worker_id))
    with open("rnaseq_expr_{0}.csv".format(worker_id), "w") as f:
        fields = ['id', 'gene_id', 'gene_name', 'transcript_id',
                  'tissue', 'bto', 'cell_type', 'level', 'expression_type',
                  'reliability', 'source']
        writer = csv.DictWriter(f, delimiter=',', quotechar='"',
                                fieldnames=fields)
        while True:
            expressions = q.get(True, 5)
            if expressions == "DONE!":
                logger.info("Worker {0} done!".format(worker_id))
                break
            for expression in expressions:
                gene_id = expression['gene_id']
                if gene_id in gene_ids:
                    expression['id'] = gene_ids[gene_id]
                    writer.writerow(expression)


def main(gem_file, rnaseq_expr_file, btoMapFile):
    logger.info("get components...")
    components = ReactionComponent.query.all()
    gene_ids = {component.long_name: component.id for component in components}
    logger.info("read bto identifiers...")
    btoMap = readBTO(btoMapFile)

    logger.info("read rnaseq expression data...")
    get_rnaseq_expressions(gene_ids, rnaseq_expr_file, btoMap)
    logger.info("read rnaseq expression data...done!")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            ("Usage: python generate_rnaseq_expr_csv.py <gem_file> "
             "<rnaseq_file> <mapBetweenTissueNameAndBTOID>")
        )
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
