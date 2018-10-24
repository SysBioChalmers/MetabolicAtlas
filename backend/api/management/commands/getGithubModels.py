import sys

import fnmatch
import re

from django.core.management.base import BaseCommand
from django.db.models import Q
from api.models import GEModel
from api.management.commands.getMAModels import insert_gems
import api.management.commands.repo_parser as repo_parser

import urllib
import urllib.request
import requests
import json

import base64


import logging

def check_PMID(PMID):
    # copied and adapted from sysomics
    try:
        int(PMID)
    except:
        return None

    url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=%s&idtype=pmid&format=json' % PMID
    r = requests.get(url)
    if not r.status_code == 200:
        return None
    json = r.json()
    if json['status'] == 'error':
        return None
    elif not json['status'] == 'ok':
        return None
    # logging.warn(json)
    doi = json['records'][0]['doi'] if 'doi' in json['records'][0] else ''
    return doi, json['records'][0]['pmid']


def get_info_from_pmid(PMID):
    # copied and adapted from sysomics
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s&format=json' % PMID
    r = requests.get(url)
    if not r.status_code == 200:
        return None
    json = r.json()
    # logging.warn(json)
    if 'error' in json['result'][PMID]:
        return None
    if 'title' in json['result'][PMID]:
        title = json['result'][PMID]['title']
    else:
        title = ''
    year = ''
    for el in json['result'][PMID]['history']:
        if el['pubstatus'] == 'pubmed':
            s_year = el['date'].split('/')[0]
            try:
                year = int(s_year)
            except:
                year = ''
            break
    return title, year


repo_parser.show_summary = False

models = GEModel.objects.all()
model_dict = {}
for model in models:
    model_dict[model.repo_name] = model.last_update

try:
    URL = 'https://api.github.com/orgs/SysBioChalmers/repos'
    result = urllib.request.urlopen(URL)
    list_repo = json.loads(result.read().decode('UTF-8'))
except Exception as e:
    logging.warn(e)
    exit(1)
    # return HttpResponse(status=400)

for repo in list_repo:
    repo_name = repo['name']
    if not repo_name.endswith('-GEM') and not repo_name.endswith('-GEMS') and not repo_name.endswith('-GEMs'):
        continue

    if repo_name == "Streptomyces_coelicolor-GEM":
        continue

    repo_updated_at = re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', repo['updated_at']).group(0)

    if repo_name in model_dict and str(model_dict[repo_name]) == repo_updated_at:
        logging.warn("repo '%s' is up-to-date, skip" % repo_name)
        continue

    logging.warn("Parsing " + repo_name)
    repo_dict = repo_parser.get_gemodel(repo_name)
    if not repo_dict:
        logging.warn("Error: cannot parse the github model %s" % repo_name)
        logging.warn(repo_parser.error_message)
        # send an email to the owner, tell him to use the parser script.
        continue

    if repo_parser.warning_messages:
        logging.warn("Warning: the github model %s have warnings:" % repo_name)
        for wm in repo_parser.warning_messages:
            logging.warn(wm)

    # get the paper, multiple papers possible?
    PMID = repo_dict['Pubmed ID']
    res = check_PMID(PMID)
    if res:
        DOI, PMID = res
        title, year = get_info_from_pmid(PMID)
        reference = {
            'title': title,
            'link': 'https://www.ncbi.nlm.nih.gov/pubmed/%s' % PMID,
            'pubmed': PMID,
            'year': year
        }

        if 'reference' in repo_dict and repo_dict['reference']:
            # '>Kerkhoven EJ, Pomraning KR, Baker SE, Nielsen J (2016) 
            # "Regulation of amino-acid metabolism controls flux
            # to lipid accumulation in _Yarrowia lipolytica_."
            # npj Systems Biology and Applications 2:16005. 
            # doi:[10.1038/npjsba.2016.5](http://www.nature.com/articles/npjsba20165)
            reference['title'] = repo_dict['reference'].strip('>').split(' doi:[')[0]
    else:
        reference = None

    description = repo_dict['Abstract']
    description = description.strip('_')
    description = re.sub('\s+_', ' ', description)
    description = re.sub('_([\s+_.,:])', '\g<1>', description)

    # build the model set, only one per repository
    model_set_data = {
        'name': repo_name.split('-GEM')[0].replace('_', ' '),
        'reference': [reference], # only one reference
        'description': description
    }

    models_to_insert = 1
    if repo_dict['Model KeyWords']['gem category'][0].lower() != 'species':
        models_to_insert = len(repo_dict['The repo contains']) - 2 # header and '----' rows

    organism = repo_dict['Model KeyWords']['taxonomy'][0]
    tissue = repo_dict['Model KeyWords']['tissue'][0] if 'tissue' in repo_dict['Model KeyWords'] else None
    cell_type = repo_dict['Model KeyWords']['cell type'][0] if 'cell type' in repo_dict['Model KeyWords'] else None
    cell_line = repo_dict['Model KeyWords']['cell line'][0] if 'cell line' in repo_dict['Model KeyWords'] else None

    model_data_list = []
    models_table = repo_dict['The repo contains']
    for i, row in enumerate(models_table):

        # default sample base on the keywords
        sample = {
            'organism': organism,
            'organ_system': '',
            'tissue': tissue,
            'cell_type': cell_type,
            'cell_line': cell_line,
        }

        model = {
            # 'gemodelset': None,  # specified upon the creation
            # 'sample': None,  # specified upon the creation
            'description': None,  # should be None, description will always be the set description
            'label': None, # TODO have a algo to generate label
            'condition': None,
            'reaction_count': 0,
            'metabolite_count': 0,
            'enzyme_count': 0,
            'files': None,
            'maintained': True,
            'reference': None,  # should be None, reference will be the set reference
            'last_update': repo_updated_at,
            'repo_name': repo_name,
        }

        if i == 0:
            keys = [column.lower() for column in row]
            continue
        elif i == 1:
            # row with '-------', maybe should be removed upon creation
            continue
        # each row is a model and a file, but can be also a new sample
        for j, col in enumerate(row):
            if keys[j].lower() == 'taxonomy':
                model_name = col.replace(' ', '_')
                sample['organism'] = col

            elif keys[j].lower() == 'tissue':
                sample['tissue'] = col
            elif keys[j].lower() == 'cell type':
                sample['cell type'] = col
            elif keys[j].lower() == 'cell line':
                sample['cell line'] = col

            elif keys[j].lower() == 'reactions':
                model['reaction_count'] = int(col)
            elif keys[j].lower() == 'metabolites':
                model['metabolite_count'] = int(col)
            elif keys[j].lower() == 'genes':
                model['enzyme_count'] = int(col)
            elif keys[j].lower() == 'strain':
                model['label'] = col
            elif keys[j].lower() == 'condition': #TESTME
                model['condition'] = col

        if not model['label']:
            model['label'] = model_name.replace('_', ' ')

        model['sample'] = sample
        files = []

        # look for SMBL files, this format should always be available
        if models_to_insert == 1:
            # model_files_found contains only 1 key, doesn't have to match the name in the table
            model_name_filename = list(repo_parser.model_files_found['xml'].keys())[0]
        else:
            # should matches model_name if not repo_parser.py must be fixed
            model_name_filename = "%s.xml" % model_name.replace(' ', '_')

        file = {
            'path': repo_parser.model_files_found['xml'][model_name_filename],
            'format': 'SBML'
        }
        files.append(file)

        # look for Matlab and Text files, these formats are optional
        for fformat, format_ext in [['Matlab', 'mat'], ['Text', 'txt']]:
            if format_ext not in repo_parser.model_files_found:
                continue

            if models_to_insert == 1:
                # model_files_found contains only 1 key
                model_name_filename = list(repo_parser.model_files_found[format_ext].keys())[0]
            else:
                model_name_filename = "%s.%s" % (model_name.replace(' ', '_'), format_ext)
            file = {
                'path': repo_parser.model_files_found[format_ext][model_name_filename],
                'format': fformat
            }
            files.append(file)

        model['files'] = files
        model_data_list.append(model)
	# FIXME the model must be delete or update, insert_gems will not update existing models
    insert_gems(model_set_data, model_data_list)


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def handle(self, *args, **options):
        pass
