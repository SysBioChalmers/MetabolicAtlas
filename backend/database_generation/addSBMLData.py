#########################################################
# the actual code to read and import the GEM SBML model #
#########################################################
import libsbml
import logging
import sys

from django.db import models
from api.models import *

import xml.etree.ElementTree as etree
import re
import collections

logger = logging.getLogger(__name__)
sh = logging.StreamHandler(stream=sys.stderr)
logger.addHandler(sh)
formatter = logging.Formatter(("%(asctime)s - %(name)s - %(levelname)s - "
                               "%(message)s"))
sh.setFormatter(formatter)
logger.setLevel(logging.INFO)

gene_no_ensembl_id = []
metabolite_no_formula = []
reaction_no_modifier = []

class SbmlAuthor(object):
    def __init__(self, sbml_model):
        annotations = sbml_model.getAnnotation()
        if annotations:
            rdf = etree.fromstring(annotations.getChild(0).toXMLString())
            self.given_name = self._get_given_name(rdf)
            self.family_name = self._get_family_name(rdf)
            self.email = self._get_email(rdf)
            self.organization = self._get_organization(rdf)
        else:
            # if no annotations on the model level then make an "empty" author object
            # this should preferably be fixed in the model though so print a message!
            self.given_name = ""
            self.family_name = ""
            self.email = ""
            self.organization = ""
            print("Error: Missing annotations for the model, so no author information will be made!")

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


def get_formula_from_notes(notes):
    """Get formula from SBML notes."""
    match = re.search(".*<p>FORMULA: ([^<]+)</p>.*", notes)
    if match:
        return match.group(1).strip()


def get_short_name_from_notes(notes):
    """Get short name from SBML notes for the proteins."""
    match = re.search(".*<p>SHORT NAME: ([^<]+)</p>.*", notes)
    if match:
        return match.group(1)


def get_subsystem_from_notes(database, notes):
    """Get sub-system name from SBML notes for the reactions."""
    match = re.search(".*<p>SUBSYSTEM: ([A-Za-z].+)</p>.*", notes)
    if match:
        name = match.group(1)
        m = re.match('.*([(](?:cytosolic|mitochondrial|peroxisomal|endoplasmic reticular)[)])$', name)
        if m:
            name = name.replace(m.group(1), '')
        name = name.strip()
        pathways = []
        # if its the HMR model its straightforward, if its yeast not so much as this is not manually curated ATM
        if name.startswith("sce"):
            names = name.split(" / ")
            eid = ""
            for n in names:
                eid = n[0:8]
                s = n[10:]
                pathway = Subsystem.objects.using(database).filter(external_id=eid)
                if not pathway:
                    pathways.append(save_pathway(database, s, eid))
                else:
                    pathways.append(pathway[0])
            return pathways
        else:
            # HMR2.0 model one subsystem per reaction only!
            pathway = Subsystem.objects.using(database).filter(name__iexact=name)
            if not pathway:
                # save_pathway is going to reformat some names
                # meaning entering this if does'nt mean the pathway is not already inserted
                # flush the table before
                pathways.append(save_pathway(database, name, ""))
            else:
                pathways.append(pathway[0])
            return pathways

    return []

def save_pathway(database, name, eid):
    sys = "Other"
    # assume that its a pathway UNLESS the name matches one of the below, or starts with 'Transport'
    # because then I will consider it a 'collection of reactions' rather than a pathway
    collec = dict([
            ("Isolated", 1),("Miscellaneous",1),("Pool reactions",1),
            ("isolated",1),("Exchange reactions ",1),("Artificial reactions",1),
            ("ABC transporters",1),("Other amino acid",1)
        ])
    aa = dict([
            ("Pyrimidine metabolism",1),("Alanine, aspartate and glutamate metabolism",1),
            ("Arginine and proline metabolism",1),("Glycine, serine and threonine metabolism",1),
            ("Lysine metabolism",1),("Tyrosine metabolism",1),("Valine, leucine, and isoleucine metabolism",1),
            ("Cysteine and methionine metabolism",1),("Thiamine metabolism",1),
            ("Tryptophan metabolism",1),("Histidine metabolism",1)
        ]);
    vitamins = dict([
            ("Folate metabolism",1),("Biotin metabolism",1),("Retinol metabolism",1),
            ("Riboflavin metabolism",1)
        ])

    if name.startswith("Fatty acid") or name.startswith("Beta oxidation"):
        sys = "Fatty acid"
    elif name in aa:
        sys = "Amino Acid metabolism"
    elif name in vitamins or name.startswith("Vitamin"):
        sys = "Vitamin metabolism"
    elif name.startswith("Glycosphingolipid"):
        sys = "Glycosphingolipid biosynthesis/metabolism"
    elif name.startswith("Carnitine shuttle"):
        sys = "Carnitine shuttle"
    elif name.startswith("Cholesterol biosynthesis"):
        sys = "Cholesterol biosynthesis"
    elif "metabolism" in name:
        sys = "Other metabolism"
        if name == "Fructose and Mannose metabolism":
            name = "Fructose and mannose metabolism"
    elif name in collec or name.startswith("Transport"):
        sys = "Collection of reactions"

    pathway = Subsystem(name=name, system=sys, external_id=eid, description="") 
    #FIXME add subsystem description
    pathway.save(using=database)
    return pathway


def get_equation(sbml_reaction):
    """Get the equation for the specified SBML reaction."""
    equation = Equation(sbml_reaction)
    return str(equation)


def get_compartment_equation(rID, rc, pc):
    rc = [el.name for el in rc]
    pc = [el.name for el in pc]
    if len(rc) == 1 and rc == pc:
        return rc[0]
    return " => ".join([" + ".join(rc), " + ".join(pc)])

def _getBound(sbml_model, paramIDAsString):
    params = sbml_model.getListOfParameters()
    for i in range(len(params)):
        p = params[i]
        if(p.getId() == paramIDAsString):
            return p.getValue()
    return -999

def get_reaction(database, sbml_model, index):
    """ Get the specified reaction from the supplied SBML model. """
    sbml_reaction = sbml_model.getReaction(index)
    reaction_to_add = Reaction(id=sbml_reaction.id)

    reaction_to_add.sbo_id = sbml_reaction.sbo_term_id
    reaction_to_add.equation = get_equation(sbml_reaction)
    # EC is specific to enzyme not reaction
    reaction_to_add.ec = get_EC_number(sbml_reaction) # FIXME store in a association table

    kinetic_law_parameters = get_kinetic_law_parameters(sbml_reaction)
    if kinetic_law_parameters:
        reaction_to_add.lower_bound = kinetic_law_parameters.get("LOWER_BOUND")
        reaction_to_add.upper_bound = kinetic_law_parameters.get("UPPER_BOUND")
        objective_coefficient = kinetic_law_parameters.get("OBJECTIVE_COEFFICIENT")
        reaction_to_add.objective_coefficient = objective_coefficient
    else:
        RFBCplg = sbml_reaction.getPlugin('fbc')
        reaction_to_add.lower_bound = _getBound(sbml_model, RFBCplg.getLowerFluxBound())
        reaction_to_add.upper_bound = _getBound(sbml_model, RFBCplg.getUpperFluxBound())

    # in order to determine which compartment the reaction takes place
    reactant_compartment = collections.OrderedDict()
    product_compartment = collections.OrderedDict()
    reactants_list = get_reaction_components(database, sbml_model, sbml_reaction.getListOfReactants())
    if not reactants_list:
        print ("Error: reactants is empty for reaction", sbml_reaction.id)
        print (sbml_reaction)
        exit(1)

    products_list = get_reaction_components(database, sbml_model, sbml_reaction.getListOfProducts())
    if not products_list:
        print ("Error: products is empty for reaction", sbml_reaction.id)
        print (sbml_reaction)
        exit(1)

    modifiers_list = get_reaction_components(database, sbml_model, sbml_reaction.getListOfModifiers())
    if not modifiers_list:
        # print ("Warning: modifiers is empty for reaction", sbml_reaction.id)
        reaction_no_modifier.append(sbml_reaction.id)
        # print (sbml_reaction)
        # exit(1)

    for currentReactant_reactioncomponent in reactants_list:
        reactant_compartment[currentReactant_reactioncomponent.compartment] = "1"
    for currentProduct_reactioncomponent in products_list:
        product_compartment[currentProduct_reactioncomponent.compartment] = "1"

    c = get_compartment_equation(sbml_reaction.id, reactant_compartment, product_compartment)
    reaction_to_add.compartment = c # FIXME this is the compartment equation, rename it
    if '=>' in c:
        reaction_to_add.is_transport = True
    reaction_to_add.is_reversible = sbml_reaction.getReversible()

    reaction_to_add.save(using=database)

    # =========================================================================================
    pathways = get_subsystem_from_notes(database, sbml_reaction.notes_string)
    for p in pathways:
        rs = SubsystemReaction.objects.using(database).filter(reaction=reaction_to_add, subsystem=p)
        if not rs:
            rs = SubsystemReaction(reaction=reaction_to_add, subsystem=p)
            rs.save(using=database)

    # add the relationship between the reaction and the compartment
    for c in reactant_compartment.keys():
        t = ReactionCompartment.objects.using(database).filter(reaction=reaction_to_add, compartment=c)
        if not t:
            rc = ReactionCompartment(reaction=reaction_to_add, compartment=c)
            rc.save(using=database)

    for c in product_compartment.keys():
        t = ReactionCompartment.objects.using(database).filter(reaction=reaction_to_add, compartment=c)
        if not t:
            rc = ReactionCompartment(reaction=reaction_to_add, compartment=c)
            rc.save(using=database)

    # add the relationship between enzymes and compartments as based on the compartment list the above uses...
    # unique list of compartments for this reaction...
    rcs = ReactionCompartment.objects.select_related('compartment').using(database).filter(reaction=reaction_to_add)
    for m in modifiers_list:
        for rc in rcs:
            t = ReactionComponentCompartment.objects.using(database).filter(component=m, compartment=rc.compartment)
            if not t:
                rcc = ReactionComponentCompartment(component=m, compartment=rc.compartment)
                rcc.save(using=database)

    # populate all the associated REACTION, and SUBSYSTEM tables
    for currentReactant_reactioncomponent in reactants_list:
        rr = ReactionReactant.objects.using(database).filter(reaction=reaction_to_add, reactant=currentReactant_reactioncomponent)
        if not rr:
            rr = ReactionReactant(reaction=reaction_to_add, reactant=currentReactant_reactioncomponent)
            rr.save(using=database)

        for p in pathways: # for yeast we currently have more than one...
            sm = SubsystemMetabolite.objects.using(database).filter(reaction_component=currentReactant_reactioncomponent, subsystem=p)
            if not sm:
                sm = SubsystemMetabolite(reaction_component=currentReactant_reactioncomponent, subsystem=p)
                sm.save(using=database)

    for currentProduct_reactioncomponent in products_list:
        rp = ReactionProduct.objects.using(database).filter(reaction=reaction_to_add, product=currentProduct_reactioncomponent)
        if not rp:
            rp = ReactionProduct(reaction=reaction_to_add, product=currentProduct_reactioncomponent)
            rp.save(using=database)

        for p in pathways: # for yeast we currently have more than one...
            sm = SubsystemMetabolite.objects.using(database).filter(reaction_component=currentProduct_reactioncomponent, subsystem=p)
            if not sm:
                sm = SubsystemMetabolite(reaction_component=currentProduct_reactioncomponent, subsystem=p)
                sm.save(using=database)

    for currentModifier_reactioncomponent in modifiers_list:
        rm = ReactionModifier.objects.using(database).filter(reaction=reaction_to_add, modifier=currentModifier_reactioncomponent)
        if not rm:
            rm = ReactionModifier(reaction=reaction_to_add, modifier=currentModifier_reactioncomponent)
            rm.save(using=database)

        for p in pathways: # for yeast we currently have more than one...
            se = SubsystemEnzyme.objects.using(database).filter(reaction_component=currentModifier_reactioncomponent, subsystem=p)
            if not se:
                se = SubsystemEnzyme(reaction_component=currentModifier_reactioncomponent, subsystem=p)
                se.save(using=database)

    return reaction_to_add


def get_kinetic_law_parameters(sbml_reaction):
    """Get kinetic law parameters for the specified SBML reaction."""
    params = {}
    kinetic_law = sbml_reaction.getKineticLaw()
    if kinetic_law:
        for i in range(kinetic_law.getNumParameters()):
            parameter = kinetic_law.getParameter(i)
            params[parameter.name] = parameter.value
        return params


def get_EC_number(sbml_reaction):
    # FIXME get only one EC but there can be multiple EC in the database
    # was this function/file updated?
    """ Get the EC number(s), if applicable, for the reaction """
    annotation = sbml_reaction.annotation_string
    if not annotation:
        return
    # match = re.search('.*ec-code:EC:(.*)["]', annotation)
    match = re.search(".*ec-code:EC:.*", annotation)
    if match:
        ec = re.sub(r'^.*ec-code:EC','EC', re.sub(r'\n','',annotation))
        ec = re.sub(r"\".*","", ec)
        return ec.replace(';EC', '; EC')


def get_reaction_components(database, sbml_model, sbml_species):
    """ Convert SBML species to a list of reaction components. """
    components_found = []
    for i in range(len(sbml_species)):
        # reaction component (enzyme and metabolite) are species in the sbml file
        species = sbml_model.getSpecies(sbml_species.get(i).species)
        components_in_db = ReactionComponent.objects.select_related('compartment').using(database).filter(id=species.id)
        if not components_in_db:
            component = ReactionComponent(id=species.id, long_name=species.name)
            component.organism = ""        # FIXME get organism from model, remove the column organism

            # FIXME atm the component type is based on long name...
            if component.long_name.startswith("ENSG"):
                component.component_type = "enzyme"
            elif not component.id.startswith("E_"):
                component.component_type = "metabolite"
            else:
                print ("Warning: invalid enzyme without Ensembl id:", component.long_name)
                gene_no_ensembl_id.append(component.long_name)
                component.component_type = "enzyme"

            component.formula = get_formula_from_notes(species.notes_string)
            if not component.formula and component.component_type == "metabolite":
                print ("Warning: invalid metabolite without formula:", component.long_name)
                metabolite_no_formula.append(component.long_name)

            component.short_name = get_short_name_from_notes(species.notes_string)
            if component.component_type == "metabolite" and component.short_name is None:
                component.short_name = component.long_name # FIXME

            if species.compartment:
                sbml_compartment = sbml_model.getCompartment(species.compartment)
                compartment = Compartment.objects.using(database).get(name=sbml_compartment.name)
                component.compartment = compartment


            components_found.append(component)
            component.save(using=database)

            # add the relationship to the compartment as well, if a metabolite!
            if component.component_type == "metabolite":
                rcc = ReactionComponentCompartment(component=component, compartment=component.compartment)
                rcc.save(using=database)
        else:
            components_found.append(components_in_db[0])
    return components_found


def addSBMLData(database, gem_file, ensembl_version, ensembl_archive_url, skip_first_reaction=0):
    doc = libsbml.readSBML(gem_file)
    print("read file: "+gem_file)
    errors = doc.getNumErrors()
    if errors != 0:
        print("Encountered {0} errors. Exiting...".format(errors))
        exit(1)

    sbml_model = doc.getModel()

    # get author and model
    logger.info("Importing model")
    if sbml_model.name == "HMRdatabase":
        pmid = "24419221"
        title="Genome-scale metabolic modelling of hepatocytes reveals serine deficiency in patients with non-alcoholic fatty liver disease"
    else:
        pmid="NA"
        title="NA"

    m = GEM.objects.using(database).filter(short_name=sbml_model.id,
        name=sbml_model.name, pmid=pmid, article_title=title,
        ensembl_version=ensembl_version, ensembl_archive_url=ensembl_archive_url)
    if not m:
        model = GEM(short_name=sbml_model.id,
            name=sbml_model.name, pmid=pmid, article_title=title,
            ensembl_version=ensembl_version, ensembl_archive_url=ensembl_archive_url)
        model.save(using=database)

    """Get author of the specified SBML model."""
    sbml_author = SbmlAuthor(sbml_model)
    print ("Author found:", sbml_author)
    a = Author.objects.using(database).filter(given_name=sbml_author.given_name,
                    family_name=sbml_author.family_name,
                    email=sbml_author.email,
                    organization=sbml_author.organization)
    if not a:
        author = Author(given_name=sbml_author.given_name,
                        family_name=sbml_author.family_name,
                        email=sbml_author.email,
                        organization=sbml_author.organization)
        author.save(using=database)

        # ma = GEMAuthor(model=model, author=author)
        # ma.save(using=database)

    # get compartments
    logger.info("Importing compartments")

    for i in range(sbml_model.getNumCompartments()):
        sbml_compartment = sbml_model.getCompartment(i)
        compartments_in_db = Compartment.objects.using(database).filter(name=sbml_compartment.name)
        if not compartments_in_db:     # only add the compartment if it does not already exists...
            compartment = Compartment(name=sbml_compartment.name)
            compartment.save(using=database)

    # get reactions
    logger.info("Importing reactions, reaction_components, and all related relationships...")
    # mr_to_add = []
    nb_reactions = sbml_model.getNumReactions()
    for i in range(nb_reactions):
        if skip_first_reaction and i < skip_first_reaction:
            continue
        if i % 1000 == 0 and i !=0:
            print ("Processing reaction # %s/%s" % (i, nb_reactions))
        reaction = get_reaction(database,sbml_model, i)
        # FIXME tmp remove GEMReaction, not used if multiple DB
        # mr = GEMReaction(model=model, reaction=reaction)
        # mr.save(using=database)
        # mr_to_add.append(mr)
    # GEMReaction.objects.bulk_create(mr_to_add)

    if gene_no_ensembl_id:
        print ("gene w/o ensembl ID:")
        print (", ".join(gene_no_ensembl_id))
    if metabolite_no_formula:
        print ("Metabolite w/o formula:")
        print (", ".join(metabolite_no_formula))
    if reaction_no_modifier:
        print ("Reaction w/o modifier:")
        print (", ".join(reaction_no_modifier))
