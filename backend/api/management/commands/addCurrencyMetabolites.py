############################################################
# the actual code to read and set the currency metabolites #
# TODO is a work in progress, do not work                  #
############################################################
from django.db.models import Count
from django.db.models import Func
from operator import itemgetter

from django.core.management.base import BaseCommand
import api.models as APImodels

class Substr(Func):
    ...
    function = 'SUBSTR'
    ...

    def as_mysql(self, compiler, connection):
        return super().as_sql(
            compiler, connection,
            function='substr',
            template="%(function)s('', %(expressions)s)",
        )

def addCurrencyMetabolites(database, currency_metabolite_file):
    reaction_without_transport = APImodels.Reaction.objects.using(database).filter(is_transport=False)
    reactants_count = APImodels.ReactionReactant.objects.using(database).filter(reaction_id__in=reaction_without_transport).values('reaction_id', 'reactant_id')

    d = {}
    reactions = {}
    for el in reactants_count:
        reactant_id = el['reactant_id']
        sub_reactant_id = reactant_id[:6]

        if sub_reactant_id not in reactions:
            reactions[sub_reactant_id] = set()
            reactions[sub_reactant_id].add(el['reaction_id'])
        elif el['reaction_id'] in reactions[sub_reactant_id]:
            continue
        else:
            reactions[sub_reactant_id].add(el['reaction_id'])

        if sub_reactant_id not in d:
            d[sub_reactant_id] = [0, set()]
        d[sub_reactant_id][0] += 1
        d[sub_reactant_id][1].add(reactant_id)
    # print (d)
    products_count = APImodels.ReactionProduct.objects.using(database).filter(reaction_id__in=reaction_without_transport).values('reaction_id', 'product_id')
    for el in products_count:
        product_id = el['product_id']
        sub_product_id = product_id[:6]

        if sub_product_id not in reactions:
            reactions[sub_product_id] = set()
            reactions[sub_product_id].add(el['reaction_id'])
        elif el['reaction_id'] in reactions[sub_product_id]:
            continue
        else:
            reactions[sub_product_id].add(el['reaction_id'])

        if sub_product_id not in d:
            d[sub_product_id] = [0, set()]
        d[sub_product_id][0] += 1
        d[sub_product_id][1].add(product_id)
    res = sorted(d.items(), key=itemgetter(1))
    # print (sorted(d.items(), key=itemgetter(1)))
    currency_ids = []
    for el in res:
        if el[1][0] > 40: # TODO remove hard-coded, must be extract from currency_metabolite_file
            currency_ids.append(el[0])

    APImodels.ReactionComponent.objects.using(database).filter(is_currency=False)
    for ID in currency_ids:
        APImodels.ReactionComponent.objects.using(database).filter(id__startswith=ID).update(is_currency=True)

    exit()

    with open(currency_metabolite_file, 'r') as f:
        for i, line in enumerate(f):
            if line.startswith('#'):
                continue
            compartment, threshold = line.strip().split('\t')
            threshold = int(threshold)
            print ('Inserting currency metabolite for %s' % compartment)


            if compartment == 'global':
                res = APImodels.Reaction.objects.using(database).raw('''
                    WITH reaction_wo_transport(id) AS (
                            select id from reaction where is_transport = false
                        ),
                        reaction_reactants_wo_transport as (
                            select * from reaction_reactants, reaction_wo_transport where reaction_id = reaction_wo_transport.id
                        ),
                        reaction_products_wo_transport as (
                            select * from reaction_products, reaction_wo_transport where reaction_id = reaction_wo_transport.id
                        ),
                        mets(id, name) as (
                            select distinct substr(id, 0, char_length(id)), short_name from reaction_component where id like 'M_m%'
                        )
                        select distinct a, mets.name, count(b) from (
                            select substr(metabolites.reaction_component, 0, 9) as a, reaction_reactants_wo_transport.reaction_id as b
                            FROM metabolites, reaction_reactants_wo_transport where
                                metabolites.reaction_component = reaction_reactants_wo_transport.reactant_id UNION ALL
                            select substr(metabolites.reaction_component, 0, 9) as a, reaction_products_wo_transport.reaction_id as b
                            FROM metabolites, reaction_products_wo_transport where
                                metabolites.reaction_component = reaction_products_wo_transport.product_id
                        ) alias1, mets where mets.id = a group by (alias1.a, mets.name) order by 3 DESC;
                        ''')
                for r in res:
                    print (r)
                #print (res)
            else:
                pass

            continue

            tokens = line.strip().split(",")
            component_id = "M_" + tokens[0]
            reaction_ids = ["R_" + reaction for reaction in tokens[1:]]
            component = APImodels.ReactionComponent.objects.using(database).filter(id=component_id)
            if not component:
                sys.exit("No component found for id "+component_id)

            for reaction_id in reaction_ids:
                reaction = Reaction.objects.using(database).filter(id=reaction_id)
                if not reaction:
                    sys.exit("No reaction found for id "+reaction_id)

                cm = APImodels.CurrencyMetabolite.objects.using(database).filter(component=component[0], reaction=reaction[0])
                if not cm:
                    cm = APImodels.CurrencyMetabolite(component=component[0], reaction=reaction[0])
                    cm.save(using=database)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('database', type=str)
        parser.add_argument('currency Met file', type=str)

    def handle(self, *args, **options):
        addCurrencyMetabolites(options['database'], options['currency Met file'])
