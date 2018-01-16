from api.models import *
from django.core.management.base import BaseCommand
import sys

def compare(type, db1, db2):
    if type == "enzyme":
        model = Enzyme
        unique_field = 'reaction_component'
    if type == "metabolite":
        model = Metabolite
        unique_field = 'reaction_component'

    return compare_model(model, unique_field, db1, db2)


def compare_model(Model, unique_field, db1, db2):

    missing_in_db1 = 0
    missing_id_db1 = []
    missing_in_db2 = 0
    missing_id_db2 = []
    modified = 0
    diff = {}

    def compare_object(e1, e2, db1, db2, diff):
        e2_dict = e2.__dict__
        for key, v in e1.__dict__.items():
            if key not in e2_dict:
                # not possible
                diff[key] = {'key deleted': True}
                continue
            if key in ['_state', 'id'] or key.endswith("_cache"):
                continue
            v = v if v else None
            e2_dict[key] = e2_dict[key] if e2_dict[key] else None
            if v == 'None' or e2_dict[key] == 'None':
                exit(1)
            if e2_dict[key] != v:
                added = 0
                deleted = 0
                modified = 0
                if not e2_dict[key]:
                    added = 1
                elif not v:
                    deleted = 1
                else:
                    modified = 1
                if key in diff:
                    diff[key] = {'added': diff[key]['added'] + added,
                                 'modified': diff[key]['modified'] + modified,
                                 'deleted': diff[key]['deleted'] + deleted
                                 }
                else:
                    diff[key] = {'added': added, 'modified': modified, 'deleted': deleted}

                print ("==========================================")
                print ("enzyme id %s (%s) is different across dbs" % (getattr(e1, unique_field), e1.id))
                print ("field '%s' (%s) : '%s'" % (key, db1, v))
                print ("field '%s' (%s) : '%s'" % (key, db2, e2_dict[key]))
        return diff

    enzyme_db1 = {}
    e1 = Model.objects.using(db1).select_related('reaction_component').all()
    for el1 in e1:
        unique_fieldv1 = getattr(el1, unique_field)
        if unique_fieldv1 in enzyme_db1:
            print ("Error: field %s %s should be unique" % (unique_field, unique_fieldv1))
            exit(1)
        enzyme_db1[unique_fieldv1] = el1
    total_db1 = len(enzyme_db1)

    enzyme_db2 = {}
    e2 = Model.objects.using(db2).select_related('reaction_component').all()
    for el2 in e2:
        unique_fieldv2 = getattr(el2, unique_field)
        if unique_fieldv2 in enzyme_db2:
            print ("Error: field %s %s should be unique" % (unique_field, unique_fieldv2))
            exit(1)
        enzyme_db2[unique_fieldv2] = el2
        if unique_fieldv2 not in enzyme_db1:
            missing_in_db1 += 1
            missing_id_db1.append(unique_fieldv2)
            print ("enzyme id %s (%s) not in database '%s'" % (unique_fieldv2, el2.id, db1))
            continue

        el1 = enzyme_db1[unique_fieldv2]
        if el2 != el1:
            modified += 1
            diff = compare_object(el1, el2, db1, db2, diff)

    total_db2 = len(enzyme_db2)

    for k in enzyme_db1:
        el1 = enzyme_db1[k]
        unique_fieldv1 = getattr(el1, unique_field)
        if unique_fieldv1 not in enzyme_db2:
            missing_in_db2 += 1
            missing_id_db2.append(unique_fieldv1)
            print ("enzyme id %s (%s) not in database '%s'" % (unique_fieldv1, el1.id, db2))
            continue

    return total_db1, total_db2, missing_in_db1, missing_id_db1, missing_in_db2, missing_id_db2, modified, diff


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def handle(self, *args, **options):
        pass

    import argparse
    parser = argparse.ArgumentParser()
    args, unknown = parser.parse_known_args()

    db1 = sys.argv[2]
    db2 = sys.argv[3]
    enz_total_db1, enz_total_db2, enz_missing_in_db1, enz_missing_id_db1, enz_missing_in_db2, enz_missing_id_db2, enz_modified, enz_diff = compare("enzyme", db1, db2)
    # met_total_db1, met_total_db2, met_missing_in_db1, met_missing_in_db2, met_modified, met_diff = compare("metabolite", db1, db2)

    print ("Compare enzyme: ===========================================")
    print ("DB1:", db1)
    print ("DB2:", db2)
    print ("total_db1", enz_total_db1)
    print ("total_db2", enz_total_db2)
    print ("missing_in_db1", enz_missing_in_db1)
    print ("missing_in_db2", enz_missing_in_db2)
    print ("modified", enz_modified)
    if enz_diff:
        for k, v in enz_diff.items():
            print ("%s : %s" % (k, v))
    print ("missing db1:")
    for el in enz_missing_id_db1:
        print (el)
    print ("missing db2:")
    for el in enz_missing_id_db2:
        print (el)

    print ("Compare metabolite: ===========================================")
    print ("DB1:", db1)
    print ("DB2:", db2)
    print ("total_db1", met_total_db1)
    print ("total_db2", met_total_db2)
    print ("missing_in_db1", met_missing_in_db1)
    print ("missing_in_db2", met_missing_in_db2)
    print ("modified", met_modified)
    if met_diff:
        for k, v in met_diff.items():
            print ("%s : %s" % (k, v))

    exit(1)

if __name__ == "__main__":
    db1 = sys.argv[1]
    db2 = sys.argv[2]
    compare_enzyme(db1, db2)