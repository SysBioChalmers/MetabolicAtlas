############################################################
# the actual code to read and set the currency metabolites #
# TODO is a work in progress, do not work                  #
############################################################
from api.models import *
from django.db.models import Count
from django.db.models import Func
from operator import itemgetter

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
    reaction_without_transport = Reaction.objects.using(database).filter(is_transport=False)
    print (reaction_without_transport.count())
    reactants_count = ReactionReactant.objects.using(database).filter(reaction_id__in=reaction_without_transport).values('reactant_id').annotate(total=Count('reactant_id')).order_by('total')
    d = {}
    for el in reactants_count:
        reactant_id = el['reactant_id']
        count = el['total']
        sub_reactant_id = reactant_id[:8]
        if sub_reactant_id not in d:
            d[sub_reactant_id] = [0, set()]
        d[sub_reactant_id][0] += int(count)
        d[sub_reactant_id][1].add(reactant_id)
    print (d)
    products_count = ReactionProduct.objects.using(database).filter(reaction_id__in=reaction_without_transport).values('product_id').annotate(total=Count('product_id')).order_by('total')
    for el in products_count:
        reactant_id = el['product_id']
        count = el['total']
        sub_product_id = reactant_id[:8]
        if sub_product_id not in d:
            d[sub_product_id] = [0, set()]
        d[sub_product_id][0] += int(count)
        d[sub_product_id][1].add(reactant_id)
    print (sorted(d.items(), key=itemgetter(1)))

    with open(currency_metabolite_file, 'r') as f:
        for i, line in enumerate(f):
            if line.startswith('#'):
                continue
            compartment, threshold = line.strip().split('\t')
            threshold = int(threshold)
            print ('Inserting currency metabolite for %s' % compartment)


            if compartment == 'global':
                res = Reaction.objects.using(database).raw('''
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
            component = ReactionComponent.objects.using(database).filter(id=component_id)
            if not component:
                sys.exit("No component found for id "+component_id)

            for reaction_id in reaction_ids:
                reaction = Reaction.objects.using(database).filter(id=reaction_id)
                if not reaction:
                    sys.exit("No reaction found for id "+reaction_id)

                cm = CurrencyMetabolite.objects.using(database).filter(component=component[0], reaction=reaction[0])
                if not cm:
                    cm = CurrencyMetabolite(component=component[0], reaction=reaction[0])
                    cm.save(using=database)


class Command(BaseCommand):

    def add_arguments(self, parser):
        import argparse
        parser.add_argument('database', type=str)
        parser.add_argument('currency-metabolite-file', type=str, default=False, dest='currency_met_file')

    def handle(self, *args, **options):
        addCurrencyMetabolites(options['database'], options['currency_met_file'])
