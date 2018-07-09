import sys
import os
import gzip
import subprocess
from django.core.management.base import BaseCommand
import api.models as APImodels

def download_file(link, output_dir):
    p = subprocess.call(["wget", "-P", output_dir, link])
    name = os.path.basename(link)
    if p == 0 and os.path.isfile(os.path.join(output_dir, name)):
        return True

    return False

def parse_hpa_xml(hpa_xml_file, output_file):
    parse_rna = False
    parse_level = False
    get_level = False
    res = {}
    with gzip.open(hpa_xml_file, 'r') as f:
        for i, line in enumerate(f):
            line = str(line.decode().strip())
            # print (line)

            if get_level:
                if line != "</data>":
                    print (line)
                    print ("Error: not data line")
                    exit(1)
                get_level = False

            if line == "</rnaExpression>":
                parse_rna = False
                continue

            if parse_level:
                arr = line.split('"')
                ttype = arr[1]
                level = float(arr[3])
                level_text = arr[4][1:].split('<')[0]
                if tissue in res[ENSEMBL_ID]:
                    print (line)
                    print ("Error: dulcated tissue %s" % tissue)
                    exit(1)
                res[ENSEMBL_ID][tissue] = [ttype, level, level_text]
                parse_level = False
                get_level = True
                continue
                # <level type="abundance" tpm="27.8">Medium</level>


            if line.startswith('<identifier id="ENSG'):
                ENSEMBL_ID = line.split('identifier id="')[1].split('"')[0]
                res[ENSEMBL_ID] = {}
                # print (ENSEMBL_ID)
                parse_rna = False

            if line == '<rnaExpression source="HPA" technology="RNAseq">':
                parse_rna = True

            if parse_rna:
                if line.startswith('<tissue>'):
                    tissue = line[8:].split('<')[0]
                    # print (tissue)
                    parse_level = True

    try:
        with open(output_file, 'w') as fw:
            i = 0
            for ENS in res:
                for tissue in res[ENS]:
                    a = res[ENS][tissue]
                    fw.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (i, ENS, tissue, a[0], a[1], a[2]))
                i += 1
    except Exception as e:
        print ("Error: cannot write HPA tabular file")
        print (e)
        exit(1)


def parse_hpa_tab(database, file):
    print (file)
    tissues_dict = {}
    level_dict = {}
    try:
        with open(file, 'r') as fh:
            i = 0
            for line in fh:
                #0   ENSG00000000003 adipose tissue  abundance   31.5    Medium
                index, gene_id, tissue, ttype, level, level_text = line.strip().split('\t')
                if gene_id not in level_dict:
                    level_dict[gene_id] = {}
                level_dict[gene_id][tissue] = level

                if tissue not in tissues_dict:
                    tissues_dict[tissue] = [float(level)]
                else:
                    tissues_dict[tissue].append(float(level))

            tissues_keys = sorted(tissues_dict.keys())

            print ("Tissue stats:")
            for i, tissue in enumerate(tissues_keys):
                minv = min(tissues_dict[tissue])
                maxv = max(tissues_dict[tissue])
                count = len(tissues_dict[tissue])
                print ("%s\t%20s %s %s %s" % (i, tissue, count, minv, maxv))
                if i != 0 and prev_count != count:
                    print ("Error: some tissue levels are not available for some genes")
                prev_count = count

            # insert the tissue and associated index in DB
            for i, tissue in enumerate(tissues_keys):
                ht = APImodels.HpaTissue.objects.using(database).filter(tissue=tissue)
                if not ht:
                    ht = APImodels.HpaTissue(index=i, tissue=tissue)
                    ht.save(using=database)

            print ("Inserting HPA expression levels..")
            for gene_id in level_dict:
                levels = []
                for tissue in tissues_keys:
                    if tissue not in level_dict[gene_id]:
                        print ("tissue %s not for %s" ^ gene_id)
                        exit(1)
                    levels.append(level_dict[gene_id][tissue])
                # insert level in DB as string, only for gene in the reaction_component list
                # check if the gene is in reaction component
                rc = APImodels.ReactionComponent.objects.using(database).filter(id=gene_id)
                if rc:
                    hpa_level = APImodels.HpaEnzymeLevel.objects.using(database).filter(rc=rc[0])
                    if not hpa_level:
                        hpa_level = APImodels.HpaEnzymeLevel(rc=rc[0], levels=','.join(levels))
                        hpa_level.save(using=database)
                #print ("%s\t%s" % (gene_id, ','.join(levels)))


    except Exception as e:
        print ("Error: cannot parse HPA tabular file")
        print (e)
        exit(1)


class Command(BaseCommand):

    def add_arguments(self, parser):
        import argparse
        parser.add_argument('database', type=str)
        parser.add_argument('--hpa-expr-file', type=str, default=False, dest='hpa_expr_file')

    def handle(self, *args, **options):
        if not options['hpa_expr_file']:
            if not os.path.isfile('/project/database_generation/proteinatlas.tsv'):
                print ("Fetching expression level from HPA..")
                # fetch file from url
                url = 'https://www.proteinatlas.org/download/proteinatlas.xml.gz'
                if not os.path.isfile('/project/database_generation/proteinatlas.xml.gz'):
                    if not download_file(url, '/project/database_generation/'):
                        print ("Error: cannot download file %s" % url)
                        exit(1)
                print("Parsing HPA xml file...")
                options['hpa_expr_file'] = '/project/database_generation/proteinatlas.tsv'
                parse_hpa_xml('/project/database_generation/proteinatlas.xml.gz', options['hpa_expr_file'])
                print ("File %s has been generated" % options['hpa_expr_file'])
            else:
                options['hpa_expr_file'] = '/project/database_generation/proteinatlas.tsv'

        print ("Parsing HPA tabular file")
        parse_hpa_tab(options['database'], options['hpa_expr_file'])
