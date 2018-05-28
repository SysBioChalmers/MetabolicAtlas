from django.core.management.base import BaseCommand
import api.models as APImodels
from django.db.models import Q


def get_mapping_model_annotation_dict(ctype):
    # dict to map header columns of annoations files to database fields
    d = {
        'metabolite': {
            'name_link': [APImodels.Metabolite, ['name_link']],
            'alt_name1': [APImodels.ReactionComponent, ['alt_name1']],
            'alt_name2': [APImodels.ReactionComponent, ['alt_name2']],
            'aliases': [APImodels.ReactionComponent, ['aliases']],
            'external_id1': [APImodels.ReactionComponent, ['external_id1']],
            'external_link1': [APImodels.Metabolite, ['external_link1']],
            'external_id2': [APImodels.ReactionComponent, ['external_id2']],
            'external_link2': [APImodels.Metabolite, ['external_link2']],
            'external_id3': [APImodels.ReactionComponent, ['external_id3']],
            'external_link3': [APImodels.Metabolite, ['external_link3']],
            'external_id4': [APImodels.ReactionComponent, ['external_id4']],
            'external_link4': [APImodels.Metabolite, ['external_link4']],
            'formula': [APImodels.ReactionComponent, ['formula']],
            'description': [APImodels.Metabolite, ['description']],
            'function1': [APImodels.Metabolite, ['function1']],
            'function2': [APImodels.Metabolite, ['function2']],
            'charge': [APImodels.Metabolite, ['charge']],
            'mass': [APImodels.Metabolite, ['mass']],
            'mass_avg': [APImodels.Metabolite, ['mass_avg']],
            'inchi': [APImodels.Metabolite, ['inchi']],
        },
        'enzyme': {
            'name': [APImodels.ReactionComponent, ['name']],
            'name_link': [APImodels.Enzyme, ['name_link']],
            'alt_name1': [APImodels.ReactionComponent, ['alt_name1']],
            'alt_name2': [APImodels.ReactionComponent, ['alt_name2']],
            'aliases': [APImodels.ReactionComponent, ['aliases']],
            'external_id1': [APImodels.ReactionComponent, ['external_id1']],
            'external_link1': [APImodels.Enzyme, ['external_link1']],
            'external_id2': [APImodels.ReactionComponent, ['external_id2']],
            'external_link2': [APImodels.Enzyme, ['external_link2']],
            'external_id3': [APImodels.ReactionComponent, ['external_id3']],
            'external_link3': [APImodels.Enzyme, ['external_link3']],
            'external_id4': [APImodels.ReactionComponent, ['external_id4']],
            'external_link4': [APImodels.Enzyme, ['external_link4']],
            'function1': [APImodels.Enzyme, ['function1']],
            'function2': [APImodels.Enzyme, ['function2']],
            'ec': [APImodels.Enzyme, ['ec']],
            'catalytic_activity': [APImodels.Enzyme, ['catalytic_activity']],
            'cofactor': [APImodels.Enzyme, ['cofactor']],
        },
        'reaction': {
            'name': [APImodels.Reaction, ['name']],
            'sbo_id': [APImodels.Reaction, ['sbo_id']],
            'ec': [APImodels.Reaction, ['ec']],
            'pmid': [APImodels.ReactionReference, ['pmid']],
        },
        'subsystem': {
            'description': [APImodels.Subsystem, ['description']],
            'system': [APImodels.Subsystem, ['system']],
            'external_id': [APImodels.Subsystem, ['external_id']],
            'external_link': [APImodels.Subsystem, ['external_link']],
        }
    }

    if ctype not in d:
        return

    annfile_model_map_dict = {}
    for model_field, v in d[ctype].items():
        model_table, file_columns = v
        for c in file_columns:
            annfile_model_map_dict[c] = [model_field, model_table]

    return annfile_model_map_dict


def reformat_list(value, separator=";"):
    arr = value.split(separator)
    sep_string = "%s " % separator # add a space after separator
    return sep_string.join([e.strip() for e in arr])



def read_annotation_file(file):
    l = []
    with open(file, 'r') as fh:
        for line in fh:
            line = line.strip('\n')
            if not line.strip() or line[0] == "#":
                continue
            elif line[0] == '@':
                # parse header
                columns = line[1:].split('\t')
            else:
                d = {}
                for i, value in enumerate(line.split('\t')):
                    if value.strip():
                        d[columns[i]] = value.strip()
                if 'ID' not in d:
                    print (d)
                    print ("Error: column 'ID' must be in the annotation file")
                    exit(1)
                if d['ID']:
                    # exclude column with empty id
                    l.append(d)
    return l


def update_metabolite(database, row_ann_dict, mapping_model_annotation_dict):
    reaction_component_dict = {}
    metabolite_dict = {}
    for file_column, value in row_ann_dict.items():
        # check if the column in the mapping dict
        if file_column == 'ID':
            continue
        if file_column not in mapping_model_annotation_dict:
            print ("Error: file column '%s' not found in mapping dictionnary" % file_column)
            exit(1)

        [model_field, model_table] = mapping_model_annotation_dict[file_column]
        if model_table == APImodels.ReactionComponent:
            if model_field in reaction_component_dict:
                print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
                exit(1)
            reaction_component_dict[model_field] = value
        else:
            if model_field in metabolite_dict:
                print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
                exit(1)
            metabolite_dict[model_field] = value

    rc = APImodels.ReactionComponent.objects.using(database).filter(id=row_ann_dict['ID'])
    if not rc:
        print ("Warning: reaction component ID '%s' not found, cannot update annotation" % row_ann_dict['ID'])
        return

    if 'aliases' in reaction_component_dict:
        reaction_component_dict['aliases'] = reformat_list(reaction_component_dict['aliases'])

    rc.update(**reaction_component_dict)
    meta = APImodels.Metabolite.objects.using(database).filter(rc=rc)
    if not meta:
        m = APImodels.Metabolite(rc=rc[0], **metabolite_dict)
        m.save(using=database)
    else:
        meta.update(**metabolite_dict)


def update_enzyme(database, row_ann_dict, mapping_model_annotation_dict):
    reaction_component_dict = {}
    enzyme_dict = {}
    for file_column, value in row_ann_dict.items():
        # check if the column in the mapping dict
        if file_column == 'ID':
            continue
        if file_column not in mapping_model_annotation_dict:
            print ("Error: file column '%s' not found in mapping dictionnary" % file_column)
            exit(1)

        [model_field, model_table] = mapping_model_annotation_dict[file_column]
        if model_table == APImodels.ReactionComponent:
            if model_field in reaction_component_dict:
                print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
                exit(1)
            reaction_component_dict[model_field] = value
        else:
            if model_field in enzyme_dict:
                print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
                exit(1)
            enzyme_dict[model_field] = value

    if 'aliases' in reaction_component_dict:
        reaction_component_dict['aliases'] = reformat_list(reaction_component_dict['aliases'])
    if 'ec' in enzyme_dict:
        enzyme_dict['ec'] = reformat_list(enzyme_dict['ec'])

    rc = APImodels.ReactionComponent.objects.using(database).filter(id=row_ann_dict['ID'])
    if not rc:
        print ("Warning: reaction component ID '%s' not found, cannot update annotation" % row_ann_dict['ID'])
        return

    rc.update(**reaction_component_dict)
    enzy = APImodels.Enzyme.objects.using(database).filter(rc=rc)
    if not enzy:
        m = APImodels.Enzyme(rc=rc[0], **enzyme_dict)
        m.save(using=database)
    else:
        enzy.update(**enzyme_dict)


def update_reaction(database, row_ann_dict, mapping_model_annotation_dict):
    reaction_dict = {}
    pmids_list = []
    for file_column, value in row_ann_dict.items():
        # check if the column in the mapping dict
        if file_column == 'ID':
            continue
        if file_column not in mapping_model_annotation_dict:
            print ("Error: file column '%s' not found in mapping dictionnary" % file_column)
            exit(1)

        [model_field, model_table] = mapping_model_annotation_dict[file_column]
        if model_table == APImodels.Reaction:
            if model_field in reaction_dict:
                print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
                exit(1)
            reaction_dict[model_field] = value

    # parse PMID
    if 'pmid' in row_ann_dict:
        pmids_list = row_ann_dict['pmid'].split(';')
    if 'ec' in reaction_dict:
        reaction_dict['ec'] = reformat_list(reaction_dict['ec'])

    r = APImodels.Reaction.objects.using(database).filter(id=row_ann_dict['ID'])
    if not r:
        print ("Warning: reaction ID '%s' not found, cannot update annotation" % row_ann_dict['ID'])
        return

    r.update(**reaction_dict)
    for pmid in pmids_list:
        pmid = pmid.strip()
        rr = APImodels.ReactionReference.objects.using(database).filter(reaction=r, pmid=pmid)
        if not rr:
            rr = APImodels.ReactionReference(reaction=r[0], pmid=pmid)
            rr.save(using=database)


def update_subsystem(database, row_ann_dict, mapping_model_annotation_dict):
    subystem_dict = {}
    for file_column, value in row_ann_dict.items():
        # check if the column in the mapping dict
        if file_column == 'ID':
            continue
        if file_column not in mapping_model_annotation_dict:
            print ("Error: file column '%s' not found in mapping dictionnary" % file_column)
            exit(1)

        [model_field, model_table] = mapping_model_annotation_dict[file_column]
        if model_field in subystem_dict:
            print ("Error: multiple columns update the field '%s' in model %s " % (model_field, model_table))
            exit(1)
        subystem_dict[model_field] = value

    s = APImodels.Subsystem.objects.using(database).filter(name=row_ann_dict['ID'])
    if not s:
        print ("Warning: subsystem name '%s' not found, cannot update annotation" % row_ann_dict['ID'])
        return

    s.update(**subystem_dict)


def insert_annotation(database, component_type, file):
    switch = {
        'metabolite': update_metabolite,
        'enzyme': update_enzyme,
        'reaction': update_reaction,
        'subsystem': update_subsystem
    }

    if component_type not in switch:
        print ("Error: invalid compoenent type '%s'" % component_type)
        exit(1)

    mapping_model_annotation_dict = get_mapping_model_annotation_dict(component_type)
    if not mapping_model_annotation_dict:
        print ("Error: couldn't get annotation mapping with component type '%s'" % component_type)
        exit(1)

    annotation_dicts = read_annotation_file(file)
    for row_ann_dict in annotation_dicts:
        switch[component_type](database, row_ann_dict, mapping_model_annotation_dict)

    # special annotations
    if component_type == "enzyme":
        # if name have been provided for enzyme, then the gene_rule of reaction can be stored with the enzyme's name
        reaction_w_modifier = APImodels.ReactionModifier.objects.using(database).values('reaction_id')
        for r in APImodels.Reaction.objects.using(database).filter(id__in=reaction_w_modifier):
            if not r.gene_rule:
                continue
            gene_rule_string = r.gene_rule
            enzyme_wo_name = []
            c = 0
            for enzyme in r.modifiers.all():
                if enzyme.name:
                    gene_rule_string = gene_rule_string.replace(enzyme.id, enzyme.name)
                    c +=1
                else:
                    enzyme_wo_name.append(enzyme.id)
            if c == r.modifiers.count():
                r.gene_rule_wname = gene_rule_string
                r.save(using=database)
            else:
                print ("Warning: cannot complete gr_rule for reaction '%s': %s have no name" % (r.id, "; ".join(enzyme_wo_name)))



class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('database', type=str)
        parser.add_argument('type', action='store')
        parser.add_argument('annotation file', action='store')

    def handle(self, *args, **options):
        database = options['database']
        if options['type'] == 'test':
            insert_annotation(database, 'metabolite', '/project/annotation/%s/test/METABOLITES.txt' % database)
            insert_annotation(database, 'enzyme', '/project/annotation/%s/test/ENZYMES.txt' % database)
            insert_annotation(database, 'reaction', '/project/annotation/%s/test/REACTIONS.txt' % database)
            insert_annotation(database, 'subsystem', '/project/annotation/%s/test/SUBSYSTEMS.txt' % database)
        elif options['type'] == 'all':
            insert_annotation(database, 'metabolite', '/project/annotation/%s/METABOLITES.txt' % database)
            insert_annotation(database, 'enzyme', '/project/annotation/%s/ENZYMES.txt' % database)
            insert_annotation(database, 'reaction', '/project/annotation/%s/REACTIONS.txt' % database)
            insert_annotation(database, 'subsystem', '/project/annotation/%s/SUBSYSTEMS.txt' % database)
        else:
            insert_annotation(database, options['type'], options['annotation file'])


