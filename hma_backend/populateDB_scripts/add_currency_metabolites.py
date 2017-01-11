import sys

from hma_backend import db
from hma_backend.models import Reaction, ReactionComponent


def main(cm_file):
    with open(cm_file, 'r') as f:
        for line in f:
            tokens = line.strip().split(",")
            component_id = "M_" + tokens[0]
            reaction_ids = ["R_" + reaction for reaction in tokens[1:]]
            component = ReactionComponent.query.get(component_id)
            for reaction_id in reaction_ids:
                reaction = Reaction.query.get(reaction_id)
                component.currency_metabolites.append(reaction)
            db.session.add(component)
        db.session.commit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(("Usage: python add_currency_metabolites.py "
               "<currency metabolites file>"))
        sys.exit(1)
    main(sys.argv[1])
