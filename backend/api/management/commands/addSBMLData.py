"""Import SBML model."""

import logging, re, sys, os
import xml.etree.ElementTree as etree
import libsbml

from django.db import *
from api.models import *

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)
sh = logging.StreamHandler(stream=sys.stderr)
logger.addHandler(sh)
formatter = logging.Formatter(("%(asctime)s - %(name)s - %(levelname)s - "
                               "%(message)s"))
sh.setFormatter(formatter)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _create_tags(self):
        readGEM("/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/HMRdatabase2_00.xml")

    def handle(self, *args, **options):
        self._create_tags()


# the below code copied from the old Flask model

class SbmlAuthor(object):
    def __init__(self, sbml_model):
        annotations = sbml_model.getAnnotation()
        rdf = etree.fromstring(annotations.getChild(0).toXMLString())
        self.given_name = self._get_given_name(rdf)
        self.family_name = self._get_family_name(rdf)
        self.email = self._get_email(rdf)
        self.organization = self._get_organization(rdf)

    def __repr__(self):
        return "{0} {1} ({2}), {3}".format(self.given_name,
                                           self.family_name,
                                           self.email,
                                           self.organization)

    def _get_given_name(self, rdf):
        return rdf[0][0][0][0][0][1].text

    def _get_family_name(self, rdf):
        return rdf[0][0][0][0][0][0].text

    def _get_email(self, rdf):
        return rdf[0][0][0][0][1].text

    def _get_organization(self, rdf):
        return rdf[0][0][0][0][2][0].text


def get_formula(notes):
    """Get formula from SBML notes."""
    match = re.search(".*<p>FORMULA: ([A-Z0-9]+)</p>.*", notes)
    if match:
        return match.group(1)
    else:
        return None

class Equation(object):
    def __init__(self, reaction):
        self.reactants = self._get_parts(reaction,
                                         reaction.getListOfReactants(),
                                         reaction.getNumReactants())
        self.products = self._get_parts(reaction,
                                        reaction.getListOfProducts(),
                                        reaction.getNumProducts())

    def _get_parts(self, reaction, parts, count):
        """Get the reactants or products involved in the specified reaction."""
        equation_parts = []
        for i in range(count):
            part = parts.get(i)
            species = reaction.model.getSpecies(part.species)
            name = species.name
            compartment = self._format_compartment(species.compartment)
            equation_parts.append((name, compartment,
                                   str(int(part.stoichiometry))))
        return equation_parts

    def __repr__(self):
        reactants = self._format_reaction_element(self.reactants)
        products = self._format_reaction_element(self.products)
        return "{0} => {1}".format(reactants, products)

    def _format_reaction_element(self, elements):
        formatted = []
        for name, compartment, stoichiometry in elements:
            if stoichiometry == "1":
                formatted.append("{0}[{1}]".format(name, compartment))
            else:
                formatted.append("{0} {1}[{2}]".format(stoichiometry,
                                                       name,
                                                       compartment))
        return " + ".join(formatted)

    def _format_compartment(self, compartment):
        match = re.search("C_([a-z])", compartment)
        if match:
            return match.group(1)
        else:
            return None


def get_equation(sbml_reaction):
    """Get the equation for the specified SBML reaction."""
    equation = Equation(sbml_reaction)
    return str(equation)


def get_author(sbml_model):
    """Get author of the specified SBML model."""
    sbml_author = SbmlAuthor(sbml_model)
    author = Author(given_name=sbml_author.given_name,
                    family_name=sbml_author.family_name,
                    email=sbml_author.email,
                    organization=sbml_author.organization)
    return author


def get_reaction(sbml_model, index):
    """ Get the specified reaction from the supplied SBML model. """
    sbml_reaction = sbml_model.getReaction(index)
    reaction_to_add = Reaction(id=sbml_reaction.id)

    reaction_to_add.sbo_id = sbml_reaction.sbo_term_id
    reaction_to_add.equation = get_equation(sbml_reaction)
    reaction_to_add.ec = get_EC_number(sbml_reaction)

    kinetic_law_parameters = get_kinetic_law_parameters(sbml_reaction)
    reaction_to_add.lower_bound = kinetic_law_parameters.get("LOWER_BOUND")
    reaction_to_add.upper_bound = kinetic_law_parameters.get("UPPER_BOUND")
    objective_coefficient = kinetic_law_parameters.get("OBJECTIVE_COEFFICIENT")
    reaction_to_add.objective_coefficient = objective_coefficient
    reaction_to_add.save() # FIXME would be nicer with a bulk save

    reactants_list = get_reaction_components(sbml_model,
                                        sbml_reaction.getListOfReactants())
    rr_to_add = []
    for currentReactant_reactioncomponent in reactants_list:
        rr = ReactionReactant(reaction=reaction_to_add, reactant=currentReactant_reactioncomponent)
        rr_to_add.append(rr)
    ReactionReactant.objects.bulk_create(rr_to_add)

    products_list = get_reaction_components(sbml_model,
                                       sbml_reaction.getListOfProducts())
    rr_to_add = []
    for currentProduct_reactioncomponent in products_list:
        rr = ReactionReactant(reaction=reaction_to_add, reactant=currentProduct_reactioncomponent)
        rr_to_add.append(rr)
    ReactionReactant.objects.bulk_create(rr_to_add)

    modifiers_list = get_reaction_components(sbml_model,
                                        sbml_reaction.getListOfModifiers())
    rr_to_add = []
    for currentModifier_reactioncomponent in modifiers_list:
        rr = ReactionReactant(reaction=reaction_to_add, reactant=currentModifier_reactioncomponent)
        rr_to_add.append(rr)
    ReactionReactant.objects.bulk_create(rr_to_add)

    return reaction_to_add


def get_kinetic_law_parameters(sbml_reaction):
    """Get kinetic law parameters for the specified SBML reaction."""
    params = {}
    kinetic_law = sbml_reaction.getKineticLaw()
    for i in range(kinetic_law.getNumParameters()):
        parameter = kinetic_law.getParameter(i)
        params[parameter.name] = parameter.value
    return params

def get_EC_number(sbml_reaction):
    """ Get the EC number(s), if applicable, for the reaction """
    annotation = sbml_reaction.annotation_string
    if annotation is None:
        return None
    match = re.search(".*ec-code:EC:.*", annotation)
    if match:
        ec = re.sub(r'^.*ec-code:EC','EC', re.sub(r'\n','',annotation))
        ec = re.sub(r"\".*","", ec)
        return ec
    else:
        return None


def get_reaction_components(sbml_model, sbml_species):
    """ Convert SBML species to a list of reaction components. """
    components_found = []
    for i in range(len(sbml_species)):
        species = sbml_model.getSpecies(sbml_species.get(i).species)
        components_in_db = ReactionComponent.objects.filter(id=species.id)
        if len(components_in_db)<1:
            component = ReactionComponent(id=species.id, long_name=species.name)
            # FIXME get organism from model
            component.organism = "Human"
            component.formula = get_formula(species.notes_string)
            if species.compartment:
                sbml_compartment = sbml_model.getCompartment(species.compartment)
                compartment = Compartment.objects.filter(name=sbml_compartment.name)
                component.compartment = compartment[0]
            # set the component type as based on long name at the moment...
            if component.long_name.startswith("ENSG0"):
                component.component_type = "enzyme"
                component.formula = ""
            else:
                component.component_type = "metabolite"
            components_found.append(component)
            component.save() # FIXME would be nicer with a bulk create!
        else:
            components_found.append(components_in_db[0])
    return components_found


def readGEM(gem_file):
    doc = libsbml.readSBML(gem_file)
    errors = doc.getNumErrors()
    if errors != 0:
        print("Encountered {0} errors. Exiting...".format(errors))
        sys.exit(1)

    sbml_model = doc.getModel()

    # get author and model
    logger.info("Importing model")
    model = MetabolicModel(short_name=sbml_model.id,
                           name=sbml_model.name)
    model.save()
    author = get_author(sbml_model)
    author.save()
    ma = ModelAuthor(model=model, author=author)
    ma.save()

    # get compartments
    logger.info("Importing compartments")
    compartments_to_add = []
    for i in range(sbml_model.getNumCompartments()):
        sbml_compartment = sbml_model.getCompartment(i)
        compartments_in_db = Compartment.objects.filter(name=sbml_compartment.name)
        if(len(compartments_in_db)<1):     # only add the compartment if it does not already exists...
            compartment = Compartment(name=sbml_compartment.name)
            compartments_to_add.append(compartment)
    Compartment.objects.bulk_create(compartments_to_add)

    # get reactions
    logger.info("Importing reactions")
    mr_to_add = []
    for i in range(sbml_model.getNumReactions()):
        reaction = get_reaction(sbml_model, i)
        mr = ModelReaction(model=model, reaction=reaction)
        mr_to_add.append(mr)
    ModelReaction.objects.bulk_create(mr_to_add)
