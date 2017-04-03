import sys, os, csv, re
from multiprocessing import Process, Queue, cpu_count
from statistics import median
import logging

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand

#NUM_CPUS = cpu_count()
NUM_CPUS=1

logger = logging.getLogger(__name__)
sh = logging.StreamHandler(stream=sys.stderr)
logger.addHandler(sh)
formatter = logging.Formatter(("%(asctime)s - %(name)s - %(levelname)s - "
                               "%(message)s"))
sh.setFormatter(formatter)
logger.setLevel(logging.INFO)


def get_rnaseq_expressions(gene_ids, rnaseq_expr_file, btoMap, outputfile):
    """Read rnaseq expressions from supplied file."""
    logger.info("Reading RNA-seq file...")
    q = Queue()
    queue_proc = Process(target=queue_rnaseq_expressions,
                         args=(q, rnaseq_expr_file, NUM_CPUS, btoMap))
    queue_proc.start()
    workers = []
    for i in range(NUM_CPUS):
        worker = Process(target=save_rnaseq_expressions, args=(i, q, gene_ids, outputfile))
        worker.start()
        workers.append(worker)
    logger.info("Reading rnaseq file...done!")


def queue_rnaseq_expressions(q, rnaseq_expr_file, num_workers, btoMap):
    """Read expressions from file and publish to a queue."""
    logger.info("RNA-seq publish expressions")
    for expressions in read_rnaseq_expressions(rnaseq_expr_file, btoMap):
        q.put(expressions)
    logger.info("Publisher done, notifying RNA-seq workers...")
    for i in range(num_workers):
        q.put("DONE!")
    logger.info("RNA-seq workers notified")


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
                expression['cell_type'] = None
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


def save_rnaseq_expressions(worker_id, q, gene_ids, outputfile):
    """Read expressions from queue and save to CSV file.

    The output file is used to import data into PostgreSQL.
    """
    logger.info("RNA-seq worker {0} started!".format(worker_id))
    with open(outputfile+"_{0}.csv".format(worker_id), "w") as f:
        fields = ['id', 'gene_id', 'gene_name', 'transcript_id',
                  'tissue', 'bto', 'cell_type', 'level', 'expression_type',
                  'reliability', 'source']
        writer = csv.DictWriter(f, delimiter=',', quotechar='"',
                                fieldnames=fields)
        while True:
            expressions = q.get(True, 5)
            if expressions == "DONE!":
                logger.info("RNA-seq worker {0} done!".format(worker_id))
                break
            for expression in expressions:
                gene_id = expression['gene_id']
                if gene_id in gene_ids:
                    expression['id'] = gene_ids[gene_id]
                    writer.writerow(expression)

def get_antibody_expressions(gene_ids, antibody_file, btoMap, outputfile):
    """Read antibody expressions from supplied file."""
    logger.info("Reading antibody file...")
    q = Queue()
    queue_proc = Process(target=queue_abp_expressions,
                         args=(q, antibody_file, gene_ids, NUM_CPUS, btoMap))
    queue_proc.start()
    workers = []
    for i in range(NUM_CPUS):
        worker = Process(target=save_abp_expression, args=(i, q, outputfile))
        worker.start()
        workers.append(worker)
    logger.info("Reading antibody file...done!")


def queue_abp_expressions(q, antibody_file, gene_ids, num_workers, btoMap):
    """Read expressions from file and publish to a queue."""
    logger.info("Publish antibody expressions")
    for expression in read_antibody_expressions(antibody_file):
        gene_id = expression['Gene']
        if gene_id in gene_ids:
            expression['id'] = gene_ids[gene_id]
            # FIXME what should we have here?
            expression['transcript_id'] = None
            # FIXME don't hardcode this
            expression['source'] = "HMA V14"
            tissue = expression['Tissue']
            tissue = re.sub(" \d$", "", tissue) # if it ends with a number like stomach 1
            if(re.match("soft ", tissue)):
                tissue = expression['Cell type']
            cell_type = expression['Cell type']
            if(cell_type in btoMap):
                expression['bto'] = btoMap[cell_type]
            else:
                nameToBTOMap = tissue + " - " + cell_type
                if(cell_type == "glandular cells"):
                    nameToBTOMap = tissue
                if(nameToBTOMap not in btoMap):
                    sys.exit("Missing bto id for combo '"+nameToBTOMap+"' in file '"+sys.argv[3]+"'.")
                expression['bto'] = btoMap[tissue]
            expression['Tissue'] = tissue + " - " + cell_type
            q.put(expression)
    logger.info("Publisher done, notifying antibody workers...")
    for i in range(num_workers):
        q.put("DONE!")
    logger.info("Antibody workers notified")


def read_antibody_expressions(antibody_file):
    """Read expressions from file."""
    with open(antibody_file, 'r') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for expression in reader:
            yield expression

def save_abp_expression(worker_id, q, outputfile):
    """Read expressions from queue and save to CSV file.

    The output file is used to import data into PostgreSQL.
    """
    logger.info("Antibody worker {0} started!".format(worker_id))
    with open(outputfile+"_{0}.csv".format(worker_id), "w") as f:
        fields = ['id', 'Gene', 'Gene name', 'transcript_id', 'Tissue',
                  'Cell type', 'bto', 'Level', 'Expression type', 'Reliability',
                  'source']
        writer = csv.DictWriter(f, delimiter=',', quotechar='"',
                                fieldnames=fields)
        while True:
            expression = q.get(True, 5)
            if expression == "DONE!":
                logger.info("Antibody worker {0} done!".format(worker_id))
                break
            writer.writerow(expression)



class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'
    folder="/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/"
    bto_map_file=folder+"mapTissueToBTO.tab"
    rnaseq_expr_file=folder+"transcript_rna_tissue.tsv"
    rnaseq_expr_file_to_make=folder+"load_rnaseq_from_HPA"
    antibody_file=folder+"normal_tissue.csv"
    antibody_file_to_make=folder+"load_antibody_from_HPA"

    def handle(self, *args, **options):
        logger.info("Get ReactionComponents from database...")
        components = ReactionComponent.objects.all()
        gene_ids = {component.long_name: component.id for component in components}
        logger.info("Read bto identifiers...")
        btoMap = readBTO(self.bto_map_file)

        logger.info("RNA-seq expression data...")
        #get_rnaseq_expressions(gene_ids, self.rnaseq_expr_file, btoMap, self.rnaseq_expr_file_to_make)
        logger.info("Antibody levels...")
        get_antibody_expressions(gene_ids, self.antibody_file, btoMap, self.antibody_file_to_make)
        logger.info("DONE!")
