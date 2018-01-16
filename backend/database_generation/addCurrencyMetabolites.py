############################################################
# the actual code to read and set the currency metabolites #
############################################################
from api.models import *

def addCurrencyMetabolites(database, cm_file):
    with open(cm_file, 'r') as f:
        for i, line in enumerate(f):
            if i != 0 and i % 100 == 0:
                print ("Processing currency metabolite %s" % i)
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
