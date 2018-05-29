#########################################################
# the actual code to read and import the GEM SBML model #
#########################################################
import yaml
import logging
import sys

from django.db import models
from api.models import *

import re
import collections

# e.g. [('id', 'm00005c'), ('name', '(11R)-HPETE'), ('compartment', 'c'), ('formula', 'C20H32O4'), ('annotation', [('lipidmaps', 'LMFA03060071')])]
# get only id, name and compartment
def make_meta_dict(info):
    d = {}
    for key, value in info:
        if key in ['id', 'name', 'compartment']:
            d[key] = value
    if len(d) != 3:
        print ("Error: missing id, name or compartment for metabolite %s" % info)
        exit(1)
    return d


def make_rxn_dict(info):
    d = {}
    d['reactant'] = []
    d['product'] = []
    for key, value in info:
        if key in ['id', 'metabolites', 'gene_reaction_rule', 'lower_bound', 'upper_bound', 'subsystem']:
            if  key == 'subsystem':
                if not isinstance(value, list):
                    # yeast have multiple subsystem, subsystem in hmr are one, string type
                    d[key] = [value]
                else:
                    d[key] = value
            elif key == 'metabolites':
                for id, stoichiometry in value:
                    if stoichiometry < 0:
                        d['reactant'].append([id, -stoichiometry])
                    else:
                        d['product'].append([id, stoichiometry])
            else:
                d[key] = value
    for key in ['id', 'reactant', 'product', 'lower_bound', 'upper_bound']:
        if key not in d:
            print ("Error: missing key '%s' for reaction %s" % (key, info))
            exit(1)
    return d


def get_modifiersID_from_GRrule(gr_rule):
    if not gr_rule:
        return []
    # FIXME do not for if gene ID contains parenthesis
    r = re.split('[\s+and\s+|\s+or\s+|(+|)+|\s+]', gr_rule)
    return [e for e in r if e]
    # return re.split('[^and|or|(|)|\s]', gr_rule)


"""
    read YAML model files and insert the strict minimum information
    Annotations should be added in a separate script
"""
def load_YAML(database, yaml_file, delete=False):
    with open(yaml_file, 'r') as fh:
        print ('Reading YAML file...')
        model_list = yaml.load(fh.read())
        metabolites, reactions, genes, compartments = model_list

    if delete:
        Compartment.objects.using(database).all().delete()

    print("Inserting compartments...")
    compartment_dict = {} 
    for letter_code, name in compartments[1]:
        compartment = Compartment.objects.using(database).filter(name__iexact=name)
        if not compartment:     # only add the compartment if it does not already exists...
            compartment = Compartment(name=name, letter_code=letter_code)
            compartment.save(using=database)
        else:
            compartment=compartment[0]
        compartment_dict[letter_code] = compartment

    if delete:
        ReactionComponent.objects.using(database).all().delete()

    print("Inserting metabolites (rc)...")
    rc_dict = {} # store reaction component pour connectivity tables (reaction/reactant, rc/subsystem, rc /compartment)
    for el in metabolites[1]:
        dict_metabolite = make_meta_dict(el)
        rc = ReactionComponent.objects.using(database).filter(id__iexact=dict_metabolite['id'])
        if not rc:
            compartment = compartment_dict[dict_metabolite['compartment']]
            rc = ReactionComponent(id=dict_metabolite['id'], name=dict_metabolite['name'], component_type='m', compartment=compartment, compartment_str=compartment.name)
            rc.save(using=database)

            # add the relationship to the compartment as well, if a metabolite!
            if rc.component_type == "m":
                rcc = ReactionComponentCompartment(rc=rc, compartment=rc.compartment)
                rcc.save(using=database)
        else:
            rc = rc[0]

        rc_dict[dict_metabolite['id']] = rc

    print("Inserting enzymes (rc)...")
    for el in genes[1]:
        id_string, id_value = el[0]
        rc = ReactionComponent.objects.using(database).filter(id__iexact=id_value)
        if not rc:
            # name should be provide in the annotation file
            # the is no compartment localization for enzyme
            rc = ReactionComponent(id=id_value, name='', component_type='e')
            rc.save(using=database)
        else:
            rc = rc[0]
        rc_dict[id_value] = rc

    if delete:
        Reaction.objects.using(database).all().delete()
        Subsystem.objects.using(database).all().delete()

    reaction_dict = {}
    print("Inserting reactions...")
    for el in reactions[1]:
        dict_rxn = make_rxn_dict(el)
        # build the reaction equation with id and the reaction equation with name
        equation = Equation(dict_rxn, rc_dict)
        equation_compartment = equation.get_equation_compartment()

        # extract additional info
        is_transport = False
        if '=>' in equation_compartment:
            is_transport = True
        is_reversible = dict_rxn['lower_bound'] == -1000
        gr_rule = dict_rxn['gene_reaction_rule'] if 'gene_reaction_rule' in dict_rxn else None

        # fix gr rule useless parenthesis
        if gr_rule and gr_rule.startswith('(') and gr_rule.endswith(')') and gr_rule.count('(') == 1 and gr_rule.count(')') == 1:
            gr_rule = gr_rule[1:-1]

        try:
            r = Reaction.objects.using(database).get(id__iexact=dict_rxn['id'])
            reaction_dict[r.id] = r
        except Reaction.DoesNotExist:
            r  = Reaction(
                    id=dict_rxn['id'],
                    equation=equation.get_equation_id(),
                    equation_wname=equation.get_equation_name(),
                    gene_rule= gr_rule,
                    lower_bound=dict_rxn['lower_bound'],
                    upper_bound=dict_rxn['upper_bound'],
                    subsystem_str = '; '.join(dict_rxn['subsystem']) if 'subsystem' in dict_rxn else None,
                    compartment=equation_compartment,
                    is_reversible=is_reversible,
                    is_transport=is_transport
                )
            r.save(using=database)
            reaction_dict[dict_rxn['id']] = r

        if 'subsystem' in dict_rxn:
            subsystems_list = []
            for subsystem in dict_rxn['subsystem']:
                # custom fix, rename (compartement name)
                # m = re.match('.*([(](?:cytosolic|mitochondrial|peroxisomal|endoplasmic reticular)[)])$', subsystem)
                # if m:
                #     subsystem = subsystem.replace(m.group(1), '')

                try:
                    sub = Subsystem.objects.using(database).get(name__iexact=subsystem)
                except Subsystem.DoesNotExist:
                    # save subsystem, just the name
                    sub = Subsystem(name=subsystem)
                    sub.save(using=database)
                subsystems_list.append(sub)

                # save reaction/subsystem relationship
                rs = SubsystemReaction.objects.using(database).filter(reaction=r, subsystem=sub)
                if not rs:
                    rs = SubsystemReaction(reaction=r, subsystem=sub)
                    rs.save(using=database)

        # add reaction/reactant relationship
        for reactant in dict_rxn['reactant']:
            rc = rc_dict[reactant[0]]
            rr = ReactionReactant.objects.using(database).filter(reaction=r, reactant=rc)
            if not rr:
                rr = ReactionReactant(reaction=r, reactant=rc)
                rr.save(using=database)

            # save subsystem/metabolite relationship for reactants
            for sub in subsystems_list:
                sm = SubsystemMetabolite.objects.using(database).filter(rc=rc, subsystem=sub)
                if not sm:
                    sm = SubsystemMetabolite(rc=rc, subsystem=sub)
                    sm.save(using=database)

            # add reaction/compartment relationship using reactants
            rcompt = ReactionCompartment.objects.using(database).filter(reaction=r, compartment=rc.compartment)
            if not rcompt:
                rcompt = ReactionCompartment(reaction=r, compartment=rc.compartment)
                rcompt.save(using=database)

        # add reaction/product relationship
        for product in dict_rxn['product']:
            rc = rc_dict[product[0]]
            rr = ReactionProduct.objects.using(database).filter(reaction=r, product=rc)
            if not rr:
                rr = ReactionProduct(reaction=r, product=rc)
                rr.save(using=database)

            # save subsystem/metabolite relationship for products
            for sub in subsystems_list:
                sm = SubsystemMetabolite.objects.using(database).filter(rc=rc, subsystem=sub)
                if not sm:
                    sm = SubsystemMetabolite(rc=rc, subsystem=sub)
                    sm.save(using=database)

            # add reaction/compartment relationship using products
            rcompt = ReactionCompartment.objects.using(database).filter(reaction=r, compartment=rc.compartment)
            if not rcompt:
                rcompt = ReactionCompartment(reaction=r, compartment=rc.compartment)
                rcompt.save(using=database)

        # add the relationship between enzymes and compartments as based on the compartment list the above uses...
        # unique list of compartments for this reaction...
        modifiers = get_modifiersID_from_GRrule(gr_rule)
        if modifiers:
            # add reaction/modifiers relationship
            for m in modifiers:
                rc = rc_dict[m]
                rm = ReactionModifier.objects.using(database).filter(reaction=r, modifier=rc)
                if not rm:
                    rm = ReactionModifier(reaction=r, modifier=rc)
                    rm.save(using=database)

                # save subsystem/enzyme relationship
                for sub in subsystems_list:
                    se = SubsystemEnzyme.objects.using(database).filter(rc=rc, subsystem=sub)
                    if not se:
                        se = SubsystemEnzyme(rc=rc, subsystem=sub)
                        se.save(using=database)

            # add compartment/modifiers relationship
            r_compts = ReactionCompartment.objects.select_related('compartment').using(database).filter(reaction=r)
            for m in modifiers:
                rc = rc_dict[m]
                for r_compt in r_compts:
                    rccompt = ReactionComponentCompartment.objects.using(database).filter(rc=rc, compartment=r_compt.compartment)
                    if not rccompt:
                        rccompt = ReactionComponentCompartment(rc=rc, compartment=r_compt.compartment)
                        rccompt.save(using=database)


class Equation(object):
    def __init__(self, reaction, meta_dict):
        self.reactants = reaction['reactant']
        self.products = reaction['product']
        self.meta_dict = meta_dict
        self.fetch_meta_info()

    def get_equation_id(self):
        reactants_string = self.format_reaction_part([id for id,b,c,d,e in self.reactants])
        products_string = self.format_reaction_part([id for id,b,c,d,e in self.products])
        return "{0} => {1}".format(reactants_string, products_string)

    def get_equation_name(self):
        reactants_string = self.format_reaction_element(self.reactants, using_name=True)
        products_string = self.format_reaction_element(self.products, using_name=True)
        return "{0} => {1}".format(reactants_string, products_string)

    def get_equation_compartment(self):
        reactants_string = self.format_reaction_part({compt for a,b,compt,d,e in self.reactants})
        products_string = self.format_reaction_part({compt for a,b,compt,d,e in self.products})
        if reactants_string != products_string:
            return "{0} => {1}".format(reactants_string, products_string)
        return reactants_string


    def format_reaction_element(self, elements, using_name=False):
        formatted = []
        for id, name, compartment, compartment_code, stoichiometry in elements:
            if using_name:
                if stoichiometry == 1:
                    formatted.append("{0}[{1}]".format(name, compartment_code))
                else:
                    formatted.append("{0} {1}[{2}]".format(stoichiometry,
                                                           name,
                                                           compartment_code))
            else:
                formatted.append(id)
        return self.format_reaction_part(formatted)

    def format_reaction_part(self, elements):
        return " + ".join(elements)

    def fetch_meta_info(self):
        self.reactants = [
                            (id,
                            self.meta_dict[id].name,
                            self.meta_dict[id].compartment.name,
                            self.meta_dict[id].compartment.letter_code,
                            stoichiometry)
                            for id, stoichiometry in self.reactants
                        ]
        self.products = [
                            (id,
                            self.meta_dict[id].name,
                            self.meta_dict[id].compartment.name,
                            self.meta_dict[id].compartment.letter_code,
                            stoichiometry)
                            for id, stoichiometry in self.products
                        ]
