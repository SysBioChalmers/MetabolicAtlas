#########################################################
# the actual code to read and import the GEM SBML model #
#########################################################

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


def get_formula_from_notes(notes):
    """Get formula from SBML notes."""
    match = re.search(".*<p>FORMULA: ([A-Z0-9]+)</p>.*", notes)
    if match:
        return match.group(1)
    else:
        return None

def get_short_name_from_notes(notes):
    """Get short name from SBML notes for the proteins."""
    match = re.search(".*<p>SHORT NAME: ([A-Z0-9]+)</p>.*", notes)
    if match:
        return match.group(1)
    else:
        return None

def get_subsystem_from_notes(notes):
    """Get sub-system name from SBML notes for the reactions."""
    match = re.search(".*<p>SUBSYSTEM: ([A-Za-z].+)</p>.*", notes)
    if match:
        name = match.group(1)
        pathways = []
        # if its the HMR model its straightforward, if its yeast not so much as this is not manually curated ATM
        if name.startswith("sce"):
            names = name.split(" / ")
            eid = ""
            for n in names:
                eid = n[0:8]
                s = n[10:]
                pathway = Subsystem.objects.filter(external_id=eid)
                if len(pathway)<1:
                    pathways.append(_addPathway(s, eid))
                else:
                    pathways.append(pathway[0])
            return pathways
        else:
            # HMR2.0 model one subsystem per reaction only!
            pathway = Subsystem.objects.filter(name=name)
            if len(pathway)<1:
                pathways.append(_addPathway(name, ""))
            else:
                pathways.append(pathway[0])
            return pathways
    else:
        return []

def _addPathway(name, eid):
    sys = "Other"
    # assume that its a pathway UNLESS the name matches one of the below, or starts with 'Transport'
    # because then I will consider it a 'collection of reactions' rather than a pathway
    collections = dict([("Isolated", 1),("Miscellaneous",1),("Pool reactions",1),
        ("isolated",1),("Exchange reactions ",1),("Artificial reactions",1),
        ("ABC transporters",1),("Other amino acid",1)])
    aa=dict([("Purine metabolism",1),("Pyrimidine metabolism",1),("Alanine, aspartate and glutamate metabolism",1),
        ("Arginine and proline metabolism",1),("Glycine, serine and threonine metabolism",1),
        ("Lysine metabolism",1),("Tyrosine metabolism",1),("Valine, leucine, and isoleucine metabolism",1),
        ("Cysteine and methionine metabolism",1),("Thiamine metabolism",1),
        ("Tryptophan metabolism",1),("Histidine metabolism",1)]);
    vitamins=dict([("Folate metabolism",1),("Biotin metabolism",1),("Retinol metabolism",1),
        ("Riboflavin metabolism",1)])
    if( name.startswith("Fatty acid") or name.startswith("Beta oxidation")):
        sys = "Fatty acid"
    elif( name in aa):
        sys = "Amino Acid metabolism"
    elif( name in vitamins or name.startswith("Vitamin") ):
        sys = "Vitamin metabolism"
    elif( name.startswith("Glycosphingolipid") ):
        sys = "Glycosphingolipid biosynthesis/metabolism"
    elif( name.startswith("Carnitine shuttle") ):
        sys = "Carnitine shuttle"
    elif( name.startswith("Cholesterol biosynthesis") ):
        sys = "Cholesterol biosynthesis"
    elif( "metabolism" in name ):
        sys = "Other metabolism"
    elif( name in collections or name.startswith("Transport")):
        sys = "Collection of reactions"
    pathway = Subsystem(name=name, system=sys, external_id=eid, description="")
    pathway.save()
    return(pathway)


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


def _getCompartmentInfo(rID, rc, pc):
    r_it = iter(rc.keys())
    r_first = next(r_it)
    if len(pc) < 1:
        return(r_first.name) # for some of the yeast reactions we only have a single reactant, I have emailed Benjamin about this...
    p_it = iter(pc.keys())
    p_first = next(p_it)
    if((len(rc)==1) & (len(pc)==1) & (r_first.name==p_first.name)):
        return(r_first.name)
    if((len(rc)==1) & (len(pc)==1) & (r_first.name!=p_first.name)):
        return(r_first.name + " => "+p_first.name)
    if((len(rc)==1) & (len(pc)==2)):
        p_second = next(p_it)
        return(r_first.name + " => " + p_first.name + " + " + p_second.name)
    if((len(rc)==2) & (len(pc)==1)):
        r_second = next(r_it)
        return(r_first.name + " + " + r_second.name + " => " + p_first.name)
    if((len(rc)==2) & (len(pc)==2)):
        r_second = next(r_it)
        p_second = next(p_it)
        return(r_first.name + " + " + r_second.name + " => " + p_first.name + " + " + p_second.name)
    if((len(rc)==3) & (len(pc)==1)):
        r_second = next(r_it)
        r_third = next(r_it)
        return(r_first.name + " + " + r_second.name + " + " + r_third.name + " => " + p_first.name)
    if((len(rc)==5) & (len(pc)==1)):
        r_second = next(r_it)
        r_third = next(r_it)
        r_fourth = next(r_it)
        r_fifth = next(r_it)
        return(r_first.name + " + " + r_second.name + " + " + r_third.name + r_fourth.name + " + " + r_fifth.name + " => " + p_first.name)
    if((len(rc)==8) & (len(pc)==1)):
        r_second = next(r_it)
        r_third = next(r_it)
        r_fourth = next(r_it)
        r_fifth = next(r_it)
        r_sixth = next(r_it)
        r_seventh = next(r_it)
        r_eight = next(r_it)
        return(r_first.name + " + " + r_second.name + " + " + r_third.name + r_fourth.name + " + " + r_fifth.name + " + " + r_sixth.name + " + " + r_seventh.name + " + " + r_eight.name + " => " + p_first.name)
    sys.exit("Missing compartment information for reaction"+rID+" with "+str(len(rc))+ " and "+str(len(pc)))

def _getBound(sbml_model, paramIDAsString):
    params = sbml_model.getListOfParameters()
    for i in range(len(params)):
        p = params[i]
        if(p.getId() == paramIDAsString):
            return p.getValue()
    return -999

def get_reaction(sbml_model, index):
    """ Get the specified reaction from the supplied SBML model. """
    sbml_reaction = sbml_model.getReaction(index)
    reaction_to_add = Reaction(id=sbml_reaction.id)

    reaction_to_add.sbo_id = sbml_reaction.sbo_term_id
    reaction_to_add.equation = get_equation(sbml_reaction)
    reaction_to_add.ec = get_EC_number(sbml_reaction)
    pathways = get_subsystem_from_notes(sbml_reaction.notes_string)

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
    reactants_list = get_reaction_components(sbml_model, sbml_reaction.getListOfReactants())
    products_list = get_reaction_components(sbml_model, sbml_reaction.getListOfProducts())
    modifiers_list = get_reaction_components(sbml_model, sbml_reaction.getListOfModifiers())
    for currentReactant_reactioncomponent in reactants_list:
        reactant_compartment[currentReactant_reactioncomponent.compartment] = "1"
    for currentProduct_reactioncomponent in products_list:
        product_compartment[currentProduct_reactioncomponent.compartment] = "1"
    c = _getCompartmentInfo(sbml_reaction.id, reactant_compartment, product_compartment)
    reaction_to_add.compartment = c
    if( re.search(r'=>', c)):
        reaction_to_add.is_transport = True

    reaction_to_add.save() # FIXME would be nicer with a bulk save
    for p in pathways:
        rs = ReactionSubsystem(reaction=reaction_to_add, subsystem=p)
        rs.save()

    # populate all the associated tables
    rr_to_add = []
    for currentReactant_reactioncomponent in reactants_list:
        rr = ReactionReactant(reaction=reaction_to_add, reactant=currentReactant_reactioncomponent)
        rr_to_add.append(rr)
    ReactionReactant.objects.bulk_create(rr_to_add)
    rp_to_add = []
    for currentProduct_reactioncomponent in products_list:
        rp = ReactionProduct(reaction=reaction_to_add, product=currentProduct_reactioncomponent)
        rp_to_add.append(rp)
    ReactionProduct.objects.bulk_create(rp_to_add)
    rm_to_add = []
    for currentModifier_reactioncomponent in modifiers_list:
        rm = ReactionModifier(reaction=reaction_to_add, modifier=currentModifier_reactioncomponent)
        rm_to_add.append(rm)
    ReactionModifier.objects.bulk_create(rm_to_add)

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
    #print("Missing <kineticLaw> information for reaction "+str(sbml_reaction))
    return None

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
            component.organism = "Human"        # FIXME get organism from model
            component.formula = get_formula_from_notes(species.notes_string)
            component.short_name = get_short_name_from_notes(species.notes_string)
            if species.compartment:
                sbml_compartment = sbml_model.getCompartment(species.compartment)
                compartment = Compartment.objects.filter(name=sbml_compartment.name)
                component.compartment = compartment[0]
            # FIXME atm the component type is based on long name...
            if component.long_name.startswith("ENSG0"):
                component.component_type = "enzyme"
            else:
                component.component_type = "metabolite"
            if component.id.startswith("M_") and component.short_name is None:
                component.short_name = component.long_name
            components_found.append(component)
            component.save() # FIXME would be nicer with a bulk create!
        else:
            components_found.append(components_in_db[0])
    return components_found

def _getEnsemblArchivePath(v):
	if(v==89):
		return 'http://May2017.archive.ensembl.org/'
	elif(v==82):
		return 'http://sep2015.archive.ensembl.org/'
	elif(v==81):
		return 'http://jul2015.archive.ensembl.org/'
	elif(v==78):
		return 'http://dec2014.archive.ensembl.org/'
	elif(v==67):
		return 'http://may2012.archive.ensembl.org/'
	elif(v==54):
		return 'http://may2009.archive.ensembl.org/'
	else:
		sys.exit("\n*******************************\nError:\n\tNot a known version map\n*******************************\n");


def addSBMLData(gem_file, db_version, db_path):
    doc = libsbml.readSBML(gem_file)
    print("read file"+gem_file)
    errors = doc.getNumErrors()
    if errors != 0:
        print("Encountered {0} errors. Exiting...".format(errors))
        #sys.exit(1)

    sbml_model = doc.getModel()

    # get author and model
    logger.info("Importing model")
    pmid = "24419221"
    title="Genome-scale metabolic modelling of hepatocytes reveals serine deficiency in patients with non-alcoholic fatty liver disease"
    if(not sbml_model.name == "HMRdatabase"):
        pmid="NA"
        title="NA"
    if not db_path:
        db_path = _getEnsemblArchivePath(db_version)
    model = GEM(short_name=sbml_model.id,
        name=sbml_model.name, pmid=pmid, article_title=title,
        ensembl_version=db_version, ensembl_archive_path = db_path)
    model.save()
    author = get_author(sbml_model)
    author.save()
    ma = GEMAuthor(model=model, author=author)
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
        mr = GEMReaction(model=model, reaction=reaction)
        mr_to_add.append(mr)
    GEMReaction.objects.bulk_create(mr_to_add)
