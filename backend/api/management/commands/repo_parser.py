#!/usr/bin/env python
import argparse
import urllib.request
import json
import base64
import time
import re
import os
import io
import logging

# Gatto: cancer models (collection)
# Manish: Bacterial models (community)
# Yarrowia_lipolytica_W29-GEM
# version 1.0.8

parser = argparse.ArgumentParser(description='Chalmers genome scale metabolic model repository validator.')
parser.add_argument('repo-name', help='A name of the remote repository or local directory (option --local-repo)')
parser.add_argument('--readme-only', action='store_true', dest="readme_only", help="check the readme file only")
parser.add_argument('--no-summary', action='store_false', dest="show_summary", help="skip the print of the summary", default=True)
parser.add_argument('--local-repo', action='store_true', dest="parse_local", help="local repository directory", default=False)
args = parser.parse_args()
argv_dict = vars(args)

repo_name = argv_dict['repo-name']
readme_only = argv_dict['readme_only']
show_summary = argv_dict['show_summary']
parse_local_repo = argv_dict['parse_local']


tree_rules = [
                {     'name': 'ModelFiles',
                      'content':
                        [{'name': 'xml', 'content': [], 'required': True, 'fpattern': '.*[.]xml$', 'type': 'dir'},
                        {'name': 'txt', 'content': [], 'required': False, 'fpattern': '.*[.]txt$', 'type': 'dir'},
                        {'name': 'mat', 'content': [], 'required': False, 'fpattern': '.*[.]mat$', 'type': 'dir'}],
                    'required': True, # at least on one the formats
                    'fpattern': None,
                    'type': 'dir',
                },
                {'name': 'ComplementaryScripts', 'content': [], 'required': False, 'fpattern': None, 'type': 'dir'},
                {'name': 'LICENSE.md', 'required': True, 'type': 'file'},
                {'name': 'README.md', 'required': True, 'type': 'file'}
            ]

# FIXME the code don't rely enough on this dict, too many hardcoded checks
default_readme_rules = {
    'category': {
                  # allow some additionnal names but alert the user
                 'brief model description': 'Brief Model Description',
                 'brief repository description': 'Brief Model Description',
                 'brief description': 'Brief Model Description',
                 'description': 'Brief Model Description',
                 'abstract': 'Abstract',
                 'model keywords': 'Model KeyWords',
                 'model keyword': 'Model KeyWords',
                 'reference': 'Reference',
                 'references': 'Reference',
                 'pubmed id': 'Pubmed ID',
                 'last update': 'Last update',
                 'the model': 'The repo contains',
                 'the models': 'The repo contains',
                 'the model contains': 'The repo contains',
                 'the repo contains': 'The repo contains',
                 'main model descriptors': 'The repo contains',
                },
    'keywords': [
        ['GEM Category', True, ['Species', 'Community', 'Collection']],
        ['Utilisation', True, 
            ['maximising product growth', 'minimising product growth', 
             'predictive simulation', 'experimental data reconstruction']
        ],
        ['Field', True, 
            ['metabolic engineering', 'bacterial community', 
            'thermodynamic modelling', 'metabolic-network reconstruction']
        ],
        ['Type of Model', True, []],
        ['Model Source', True, []],
        ['Omic Source', True, []],
        ['Taxonomy', True, []],
        ['Metabolic System', True, []],
        ['Tissue', False, []],
        ['Bioreactor', False, []],
        ['Condition', True, []],
        ['Enzymatically Constrained', False, []],
        ['Cell Type', False, []],
        ['Cell Line', False, []],
        ['Strain', False, []]
    ],
    'model_table_header': {
        'Taxonomy',
        'Template Model',
        'Genes', 'Reactions', 'Metabolites'
    }
}

error_message = ''
warning_messages = []
gem_category = ''
model_files_found = {}
table_CCTS = { 
                 'cell line': False,
                 'cell type': False,
                 'tissue': False,
                 'strain': False,
             }
PMID_cat_found = False


def check_model_file_content(content):
    # check the xml file content
    pass


def check_model_files(model_dir, name, rule):
    global error_message
    global model_files_found
    print ("Checking '%s'" % name)
    if model_dir['type'] != rule['type']:
         error_message = "Error: invalid format, '%s' is expected to be %s" % (
             name, rule_dir['type'])
         return False

    mfl = {}
    if not parse_local_repo:
        URL = model_dir['url'] 
        success, model_files_json = get_json(URL)
        if not success:
            return False

        if not model_files_json and rule['required']:
            error_message = "Error: directory '%s' is empty" % name
            return False

        if rule['fpattern']:
            for element in model_files_json:
                if not re.match(rule['fpattern'], element['name']):
                    error_message = "Error: model file name '%s' is invalid, expected '%s' extension" % (element['name'], name)
                    return False
                if element['size'] == 0:
                    error_message = "Error: model file '%s' is empty" % element['name']
                    return False
                if element['type'] != 'file':
                    error_message = "Error: model file '%s' is not a file" % element['name']
                    return False
                mfl[element['name']] = element['download_url']
            model_files_found[name] = mfl
    else:
        if rule['fpattern']:
            for element in os.listdir(model_dir['path']):
                full_path = os.path.join(model_dir['path'], element)
                if not re.match(rule['fpattern'], element):
                    error_message = "Error: model file name '%s' is invalid, expected '%s' extenion" % (element, name)
                    return False
                if not os.path.isfile(full_path):
                    error_message = "Error: model file '%s' is not a file" % element
                    return False
                if os.path.getsize(full_path) == 0:
                    error_message = "Error: model file '%s' is empty" % element
                    return False
                mfl[element] = None
            model_files_found[name] = mfl
    return True


def check_models_dirs(model_dir, name, rule_dir):
    global warning_messages
    global error_message
    print ("Checking directory '%s'" % name)
    if model_dir['type'] != rule_dir['type']:
         error_message = "Error: invalid format, '%s' is expected to be %s" % \
         (name, rule_dir['type'])
         return False

    content = {}
    if not parse_local_repo:
        URL = model_dir['url']
        success, model_dirs_json = get_json(URL)
        if not success:
            return False

        for element in model_dirs_json:
            content[element['name']] = element
    else:
        for name in os.listdir(model_dir['path']):
            if name[0] == '.':
                continue
            full_path = os.path.join(model_dir['path'], name)
            content[name] = {
                'type': 'dir' if os.path.isdir(full_path) else 'file',
                'size': os.path.getsize(full_path),
                'name': name,
                'path': full_path
                }

    for rule in rule_dir['content']:
        name = rule['name']
        type = rule['type']
        required = rule['required']
        if name not in content:
            if required:
                error_message = "Error: %s '%s' not found" % (type, name)
                return False
            else:
                warning_messages.append("Warning: %s '%s' not found" % (type, name))
                return False
        else:
            if not check_model_files(content[name], name, rule):
                return False
    return True


def check_repo_content(repo_content):
    global warning_messages
    global error_message
    content = {}
    if not parse_local_repo:
        for element in repo_content:
            content[element['name']] = element
    else:
        # repo_content = repo path
        for name in os.listdir(repo_content):
            if name[0] == '.':
                continue
            full_path = os.path.join(repo_content, name)
            content[name] = {
                'type': 'dir' if os.path.isdir(full_path) else 'file',
                'size': os.path.getsize(full_path),
                'name': name,
                'path': full_path
                }

    for rule in tree_rules:
        type = rule['type']
        name = rule['name']
        required = rule['required']
        if name not in content:
            if required:
                error_message = "Error: %s '%s' not found" % (type, name)
                return False
            else:
                warning_messages.append("Warning: %s '%s' not found" % (type, name))
        else:
            rmt_name = content[name]['name']
            rmt_type = content[name]['type']
            rmt_size = content[name]['size']
            if type != rmt_type:
                error_message = "Error: '%s' is %s, expected %s" % (name, rmt_type, type)
                return False
            if type == 'file':
                if not rmt_size:
                    if required:
                        error_message = "Error: file '%s' is empty" % name
                        return False
                    else:
                        warning_messages.append("Warning: file '%s' is empty" % name)
                        return False
            elif type == 'dir'and rmt_name == "ModelFiles":
                if not check_models_dirs(content[name], rmt_name, rule):
                    return False
    return True


def check_local_repo_content(local_repo):
    content = {}
    for name in os.listdir(local_repo):
        if name[0] == '.':
            continue
        full_path = os.path.join(local_repo, name)
        content[name] = {
            'type': 'dir' if os.path.isdir(full_path) else 'file',
            'size': os.path.getsize(full_path)
            }


    for rule in tree_rules:
        type = rule['type']
        name = rule['name']
        required = rule['required']


def parse_readme_file(content):
    global error_message
    readme_dict = {}
    parse_category = False
    found_model_table = False
    model_table = []
    cat = False;
    for line in content.decode('UTF-8').split('\n'):
        line = line.strip()
        if line.startswith("- ") or line.startswith("* "):
            parse_category = True
            if cat:
                readme_dict[cat] = re.sub("\s{2,}", " ", readme_dict[cat])
            # new cat
            cat_value = line[2:].split(":")
            if len(cat_value) == 2:
                cat, value = (el.strip() for el in cat_value)
            else:
                cat = cat_value[0].strip()
                value = ""
            readme_dict[cat] = value
        elif parse_category:
            if "the model" in cat.lower() or \
                "the repo" in cat.lower() or \
                 "main model descriptors" in cat.lower(): # try to get the model table
                if re.match('^[|](?:[^|]+[|]){5,7}', line):
                    found_model_table = True
                    model_table.append([el.strip() for el in line.strip('|').split('|')])
                elif found_model_table:
                    readme_dict[cat] = model_table
                    break
            else:
                readme_dict[cat] += line.strip()
    if not found_model_table:
        error_message = "Error: couldn't  fine the models table" % name
    return readme_dict


def parse_categories(readme_dict):
    global warning_messages
    global error_message
    required_cat = {v for v in default_readme_rules['category'].values()}
    new_categories = {}
    for name, content in readme_dict.items():
        if name.lower() not in default_readme_rules['category']:
            warning_messages.append("Warning: unknown readme category '%s'" % name)
        else:
            correct_name = default_readme_rules['category'][name.lower()]
            if correct_name not in required_cat:
                error_message = "Error: category '%s' is duplicated" % name
                return False
            required_cat.remove(correct_name)
            if correct_name != name:
                warning_messages.append("Warning: category '%s' should be renamed '%s'" % (name, correct_name))
            if not content:
                error_message = "Error: category '%s' seems empty" % name
                return False
            new_categories[correct_name] = content
    # if no paper
    for cat in ['Abstract', 'Reference', 'Pubmed ID']:
        if cat in required_cat:
            new_categories[cat] = ''
            required_cat.remove(cat)

    if required_cat:
        # TODO check PMID_cat_found
        error_message = "Error: categories not found: %s" % \
            ", ".join(["'%s'" % c for c in required_cat])
        return False
    return new_categories


def reformat_keywords(keywords_string):
    global gem_category
    global error_message
    keywords_string = keywords_string.strip()
    if not keywords_string:
        error_message = "Error: keywords string seems empty"
        return False

    try:
        kw = [el for el in keywords_string.strip('**').split('; **')]
        kw = dict(el.split(":**")[:2] if ":**" in el else (el, "") for el in kw)
        kw = dict((k.strip(" *").lower(), v.strip(" ;")) for k, v in kw.items())
    except Exception as e:
        print (e)
        error_message = "Error: cannot parse keywords string"
        return False

    # extract the GEM category, needed to parse the model table
    if 'gem category' not in kw:
        error_message = "Error: missing keyword 'GEM Category'"
        return False
    elif kw['gem category'] not in default_readme_rules['keywords'][0][2]:
        error_message = "Error: invalid keyword value '%s' for 'GEM Category', choices are %s" % \
            (kw['gem category'], ", ".join(default_readme_rules['keywords'][0][2]))
        return False
    else:
        gem_category = kw['gem category']
    return kw


def parse_keywords(kw_dict):
    global warning_messages
    global error_message
    found_tissue = False
    found_bioreactor = False
    # print (kw_dict)
    for name, require, require_content in default_readme_rules['keywords']:
        kw_lower_name = name.lower()
        if require and (kw_lower_name not in kw_dict or not kw_dict[kw_lower_name]):
            error_message = "Error: keyword '%s' not found " % name
            return False
        elif require_content and kw_dict[kw_lower_name].lower() not in [el.lower() for el in require_content]:
            list_choice = [e.strip() for e in kw_dict[kw_lower_name].lower().split(',')]
            if len(list_choice) > 1:
                # check each choice against the white list
                for c in list_choice:
                    if c not in [el.lower() for el in require_content]:
                        error_message = "Error: invalid keyword value '%s' for '%s', choices are %s" % \
                            (c, name, ", ".join(require_content))
                        return False
            else:
                error_message = "Error: invalid keyword value '%s' for '%s', choices are %s" %  \
                    (kw_dict[kw_lower_name], name, ", ".join(require_content))
                return False
        elif kw_lower_name in ['cell type', 'cell line', 'tissue', 'strain']:
            if (kw_lower_name not in kw_dict or not kw_dict[kw_lower_name]) and \
                not table_CCTS[kw_lower_name]:
                warning_messages.append("Warning: keyword value for '%s' is empty and not found in the model(s) table" % name)
            elif (kw_lower_name in kw_dict and kw_dict[kw_lower_name]) and \
                table_CCTS[kw_lower_name]:
                error_message = "Error: keyword '%s' should not be defined in both keyword list and model(s) table" % name
                return False
        elif kw_lower_name == 'tissue' and 'tissue' in kw_dict and kw_dict['tissue']:
            found_tissue = True
        elif kw_lower_name == 'bioreactor' and 'bioreactor' in kw_dict and kw_dict['bioreactor']:
            found_bioreactor = True

        if kw_lower_name in kw_dict:
            kw_dict[kw_lower_name] = [el.strip() for el in kw_dict[kw_lower_name].split(';') if el.strip()]

    if (found_tissue or table_CCTS['tissue']) and found_bioreactor:
        # FIXME
        error_message = "Error: choose between fields Bioreactor or Tissue"
        return False

    return kw_dict


def parse_model_table(model_array):
    global table_CCTS
    global warning_messages
    global error_message
    if len(model_array) < 3:
        error_message = "Error: the model table seems empty"
        return False
    elif gem_category == "Species" and len(model_array) != 3:
        error_message = "Error: the model table should contains only one row for GEM category 'Species'"
        return False
    if not readme_only and len(model_files_found['xml']) != len(model_array) - 2:
        error_message = "Error: the number of models described in the table " + \
            "do not match the number of models in the 'xml' directory"
        return False
    header = []
    model_info_dict = {}
    for i, row in enumerate(model_array):
        if i == 0:
            header = row
            missing_col = {v.lower() for v in default_readme_rules['model_table_header']} - \
                set([h.lower() for h in header])
            if missing_col:
                error_message = "Error: the model(s) table columns are missing: %s" % \
                    ", ".join(["'%s'" % c for c in missing_col])
                return False
            for h in [h.lower() for h in header if h.lower() in ['cell type', 'cell line', 'tissue', 'strain']]:
                table_CCTS[h] = True
            continue
        elif i == 1:
            continue
        for j, h in enumerate(header):
            if not row[j]:
                warning_messages.append("Warning: empty cell in model(s) table, row %s, column '%s'" % (i, header[j]))
            if h.lower() == "taxonomy":
                row_model = row[j]
                if not readme_only and gem_category != "Species" and \
                    "%s.xml" % row_model.replace(' ', '_') not in model_files_found['xml']:
                    error_message = "Error: model name '%s' do not have a xml file" % row_model
                    return False
            elif h.lower() in ['reactions', 'genes', 'metabolite']:
                try:
                    a = int(row[j])
                    if a < 0:
                        error_message = "Error: invalid value '%s' (column '%s') for model '%s', expected a number >= 0" % \
                            (row[j], header[j], row_model)
                        return False
                except:
                    error_message = ("Error: invalid value '%s' (column '%s') for model '%s', expected a number" % \
                        (row[j], header[j], row_model))
                    return False
            model_info_dict[row_model] = row[j]
    return model_info_dict


def get_json(URL):
    try:
        time.sleep(1)
        result = urllib.request.urlopen(URL)
        j_son = json.loads(result.read().decode('UTF-8'))
        return True, j_son
    except Exception as e:
        return False, e


def get_gemodel(repo_name):
    global warning_messages
    global error_message
    warning_messages = []
    error_message = ''

    if not parse_local_repo:
        if not repo_name.endswith('-GEM') and not (repo_name.endswith('-GEMS') or repo_name.endswith('-GEMs')):
            error_message = "Error: invalid repo name '%s', it should end with '-GEM' or '-GEMS'"
            return False

        # TODO add parsing local directory
        URL = 'https://api.github.com/repos/SysBioChalmers/' + repo_name
        success, repo_json = get_json(URL)
        if not success:
            error_message = "Error: repo '%s' does not exist or is private" % repo_name
            return False

        if 'name' not in repo_json:
            error_message = "Error: something went wrong, cannot get repository data from github"
            return False

    if not readme_only:
        # get the directory content
        if not parse_local_repo:
            URL = 'https://api.github.com/repos/SysBioChalmers/%s/contents/' % repo_json['name']
            success, repo_content = get_json(URL)
            if not success:
                error_message = "Error: cannot read repo content"
                return False
        else:
            repo_content = os.path.abspath(repo_name)

        res = check_repo_content(repo_content)
        if not res:
            error_message = "Error: invalid repository content"
            return False

    # parse the readme file
    if not parse_local_repo:
        URL = 'https://api.github.com/repos/SysBioChalmers/' + repo_name + "/contents/README.md?ref=master"
        success, readme_meta_json = get_json(URL)
        if not success:
            error_message = "Error: cannot read the README.md file"
            return False

        readme_content = base64.b64decode(readme_meta_json['content'])
    else:
        readme_file = os.path.join(repo_name, "README.md")

        if not readme_only and (not os.path.exists(readme_file) or not os.path.isfile(readme_file)):
            error_message = "Error: the README.md file does not exist or is not a file"
            return False

        with io.open(readme_file, 'r', encoding='utf8') as fh:
            readme_content = fh.read()

        if not readme_content:
            error_message = "Error: the README.md file is empty"
            return False

        readme_content = readme_content.encode('UTF-8')

    readme_dict = parse_readme_file(readme_content)
    if not readme_dict:
        # print ('here')
        return False

    cat_dict = parse_categories(readme_dict)
    if not cat_dict:
        # print ('here2')
        return False

    keywords_dict = reformat_keywords(cat_dict["Model KeyWords"])
    if not keywords_dict:
        # print ('here3')
        return False

    model_info_dict = parse_model_table(cat_dict["The repo contains"])
    if not model_info_dict:
        # print ('here4')
        return False

    keywords_dict = parse_keywords(keywords_dict)
    if not keywords_dict:
        # print ('here5')
        return False

    cat_dict['Model KeyWords'] = keywords_dict
    print ("\nSuccess: the repository is valid\n")
    if show_summary:
        print ("====================== Summary: ======================")
        for key, value in cat_dict.items():
            if key == "The repo contains":
                print ("### %s(s) ###" % key)
                if len(value) > 7:
                    print ("(Showing only the first 5 models")
                for i, model in enumerate(value[2:7], start=2):
                    for k, f in enumerate(value[0]):
                        print ("\t%-15s\t%s" % (f, value[i][k]))
                    if i < 2:
                        print ("\t----------------------")
            elif key == "Model KeyWords":
                print ("### KeyWords ###")
                for k, v in value.items():
                    print ("\t{%s}" % k)
                    print ("\t\t%s" % v) if isinstance(v, str) else \
                        [print ("\t\t%s" % el) for el in v]
            else:
                print ("### %s ###" % key)
                print ("\t%s\n" % value)

    return cat_dict


if __name__ == "__main__":
    get_gemodel(repo_name)
    for wm in warning_messages:
        print (wm)
    print (error_message)


# README 3 examples
# No PMID category in the collections / community readme type
# collection has category 'The models' while the others have 'The models contain'
# pas de reference pour community?

# SOP
# If a modeller has participated in a project that requires many versions of the same model then:
# Upload SBML GEM files in one folder called "xml"
# Upload Text GEM files in a separate folder called "ModelFiles_txt" should be "txt"

# RULE
# keyword cap sensitive
# tissue / bioreaction in the keyword list ? can be in the table ?
# when collection/commu always more than 1 ?
