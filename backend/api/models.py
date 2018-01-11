from django.db import models

#
# From gems db
#

class GEModelReference(models.Model):
    title = models.TextField()
    link = models.TextField()
    pubmed = models.CharField(max_length=20, unique=True, null=True)
    year = models.CharField(max_length=4)

    class Meta:
        db_table = "gemodelreference"


class GEModelSet(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True)
    reference = models.ManyToManyField(GEModelReference, related_name='gemodelset_references')

    class Meta:
        db_table = "gemodelset"


class GEModelSample(models.Model):
    organism = models.CharField(max_length=200)
    organ_system = models.CharField(max_length=200, null=True)
    tissue = models.CharField(max_length=200, null=True)
    cell_type = models.CharField(max_length=200, null=True)
    cell_line = models.CharField(max_length=200, null=True)

    unique_together = (('organism', 'organ_system', 'tissue', 'cell_type', 'cell_line'),)

    class Meta:
        db_table = "gemodelsample"


class GEModelFile(models.Model):
    path = models.CharField(max_length=200, unique=True)
    format = models.CharField(max_length=50)

    class Meta:
        db_table = "gemodelfile"


class GEModel(models.Model):
    gemodelset = models.ForeignKey(GEModelSet, default=1)
    sample = models.ForeignKey(GEModelSample, default=1)
    description = models.TextField(null=True)
    label = models.CharField(max_length=200, null=True)
    reaction_count = models.IntegerField(default=0)
    metabolite_count = models.IntegerField(default=0)
    enzyme_count = models.IntegerField(default=0)
    files = models.ManyToManyField(GEModelFile, related_name='gemodel_files')
    maintained = models.BooleanField(default=False)
    ref = models.ManyToManyField(GEModelReference, related_name='gemodels_refs', blank=True)

    def save(self, *args, **kwargs):
        if not self.gemodelset:
            raise AttributeError("Model set must me specify")
        if not self.sample:
            raise AttributeError("Model sample must me specify")
        # if not self.reaction_count:
        #    raise AttributeError("reaction count cannot be 0")
        # if not self.metabolite_count:
        #    raise AttributeError("metabolite count cannot be 0")
        # if not self.enzyme_count:
        #    raise AttributeError("enzyme count cannot be 0")
        super(GEModel, self).save(*args, **kwargs)

    class Meta:
        db_table = "gemodel"


##########################################################################################################################
##########################################################################################################################
#
# Extra "annotation" models, such as BTO mappings
#
class TissueOntology(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=95, unique=True)
    definition = models.CharField(max_length=7000, null=True)

    class Meta:
        db_table = "tissue_ontology"


##########################################################################################################################
##########################################################################################################################
#
# Models
#

class GEM(models.Model):
    short_name = models.CharField(max_length=255, blank=False)
    name = models.CharField(max_length=255, blank=False)
    pmid = models.CharField(max_length=11, blank=False)
    article_title = models.CharField(max_length=255, blank=False)
    ensembl_version = models.CharField(max_length=50, null=True) # keep track of this... for HMR2 make an educated guess!
    ensembl_archive_url = models.CharField(max_length=50, null=True)

    def __str__(self):
        return "<GEM: {0}>".format(self.short_name)

    class Meta:
        db_table = "gems"

class Author(models.Model):
    given_name = models.CharField(max_length=255, blank=False)
    family_name = models.CharField(max_length=255, blank=False)
    email = models.CharField(max_length=255, blank=False)
    organization = models.CharField(max_length=255, blank=False)
    models = models.ManyToManyField(GEM, related_name='authors', through='GemAuthor')

    def __str__(self):
        return "<Author: {0} {1}>".format(self.given_name, self.family_name)

    class Meta:
        db_table = "author"

class Reaction(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    sbo_id = models.CharField(max_length=50)
    equation = models.TextField(blank=False)
    ec = models.CharField(max_length=255, null=True)
    lower_bound = models.FloatField()
    upper_bound = models.FloatField()
    objective_coefficient = models.FloatField(null=True)
    #subsystem = models.CharField(max_length=600)
    compartment = models.CharField(max_length=255)
    is_transport = models.BooleanField(default=False)

    models = models.ManyToManyField(GEM, related_name='reactions', through='GemReaction')

    def __str__(self):
        return "<Reaction: {0} {1}>".format(self.id, self.modifiers)

    class Meta:
        db_table = "reaction"

class ReactionReference(models.Model):
    reaction = models.ForeignKey('Reaction', db_column='reaction_id', on_delete=models.CASCADE)
    pmid = models.CharField(max_length=25, blank=False)

    def __str__(self):
        return "<ReactionReference: {0}={1}>".format(self.reaction.id, self.pmid)

    class Meta:
        db_table = "reaction_reference"
        unique_together = (('reaction', 'pmid'),)

class ReactionComponent(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    short_name = models.CharField(max_length=255, null=True)     # when adding metabolites from the SBML model they dont have short names...
    long_name = models.CharField(max_length=255)
    component_type = models.CharField(max_length=50, db_index=True)
    organism = models.CharField(max_length=255)
    formula = models.CharField(max_length=255, null=True)        # only metabolites have this!
    compartment = models.ForeignKey('Compartment', db_column='compartment', blank=True)

    reactions_as_reactant = models.ManyToManyField(Reaction, related_name='reactants', through='ReactionReactant')
    reactions_as_product = models.ManyToManyField(Reaction, related_name='products', through='ReactionProduct')
    reactions_as_modifier = models.ManyToManyField(Reaction, related_name='modifiers', through='ReactionModifier')
    currency_metabolites = models.ManyToManyField(Reaction, related_name='currency_metabolites', through='CurrencyMetabolite')

    def __str__(self):
        return "<ReactionComponent: {0}>".format(self.id)

    class Meta:
        db_table = "reaction_component"

class ReactionComponentAnnotation(models.Model):
    component = models.ForeignKey('ReactionComponent', db_column='component_id', on_delete=models.CASCADE)
    annotation_type = models.CharField(max_length=50)
    annotation = models.CharField(max_length=5000) # some of the uniprot fields are quite long!

    def __str__(self):
        return self.component.id+"="+self.annotation_type+":"+self.annotation

    class Meta:
        db_table = "reaction_component_annotations"
        unique_together = (('component', 'annotation_type', 'annotation'),)

class Compartment(models.Model):
    name = models.CharField(max_length=50, unique=True)
    nr_reactions = models.IntegerField(default=0)
    nr_subsystems = models.IntegerField(default=0)
    nr_metabolites = models.IntegerField(default=0)
    nr_enzymes = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "compartment"

class CompartmentSvg(models.Model):
    display_name = models.CharField(max_length=25, unique=True)
    compartment = models.ForeignKey('Compartment', on_delete=models.CASCADE)
    filename = models.CharField(max_length=35)
    nr_reactions = models.IntegerField(default=0)
    nr_subsystems = models.IntegerField(default=0)
    nr_metabolites = models.IntegerField(default=0)
    nr_enzymes = models.IntegerField(default=0)

    class Meta:
        db_table = "compartmentsvg"

class ExpressionData(models.Model):
    reaction_component = models.ForeignKey('ReactionComponent', db_column='reaction_component', on_delete=models.CASCADE)
    gene_id = models.CharField(max_length=35)
    gene_name = models.CharField(max_length=255)
    transcript_id = models.CharField(max_length=35, null=True)
    tissue = models.CharField(max_length=100)
    bto = models.ForeignKey('TissueOntology', on_delete=models.DO_NOTHING) # FIXME on_delete should be no addReactionComponentAnnotation
    cell_type = models.CharField(max_length=255, null=True)
    level = models.CharField(max_length=30)
    expression_type = models.CharField(max_length=35)
    reliability = models.CharField(max_length=35)
    source = models.CharField(max_length=45)

    class Meta:
        db_table = "expression_data"
        unique_together = (('id', 'transcript_id', 'tissue', 'cell_type', 'expression_type', 'source'),)

class Metabolite(models.Model):
    reaction_component = models.OneToOneField(
            'ReactionComponent',
            related_name='metabolite',
            db_column='reaction_component',
            on_delete=models.CASCADE)
    hmdb = models.CharField(max_length=12, null=True)
    formula = models.CharField(max_length=50, null=True)
    charge = models.FloatField(null=True)
    mass = models.FloatField(null=True)
    mass_avg = models.FloatField(null=True)
    kegg = models.CharField(max_length=50, null=True)
    chebi = models.CharField(max_length=50, null=True)
    inchi = models.CharField(max_length=255, null=True)
    bigg = models.CharField(max_length=75, null=True)
    hmdb_description = models.CharField(max_length=5000, null=True)
    hmdb_link = models.CharField(max_length=255, null=True)
    pubchem_link = models.CharField(max_length=255, null=True)
    hmdb_name = models.CharField(max_length=255, null=True)
    hmdb_function = models.CharField(max_length=2000, null=True)

    class Meta:
        db_table = "metabolites"

class Enzyme(models.Model):
    reaction_component = models.OneToOneField('ReactionComponent',
        related_name='enzyme', db_column='reaction_component')
    uniprot_acc = models.CharField(max_length=35)
    protein_name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=75)
    ec = models.CharField(max_length=100, null=True)
    ncbi = models.CharField(max_length=125, null=True)
    function = models.CharField(max_length=20000, null=True)
    catalytic_activity = models.CharField(max_length=2000, null=True)
    # uniprot_link = models.CharField(max_length=255, null=True) # if the UniProt link is not valid, then something is wrong!
    ensembl_link = models.CharField(max_length=255, null=True) # should link to the RIGHT Ensembl version, otherwise leave as null...

    class Meta:
        db_table = "enzymes"


class Subsystem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    system = models.CharField(max_length=100)
    external_id = models.CharField(max_length=25, null=True)
    description = models.CharField(max_length=255, null=True)
    nr_reactions = models.IntegerField(default=0)
    nr_metabolites = models.IntegerField(default=0)
    nr_enzymes = models.IntegerField(default=0)
    nr_compartment = models.IntegerField(default=0)

    class Meta:
        db_table = "subsystems"

class SubsystemSvg(models.Model):
    name = models.CharField(max_length=100, unique=True)
    system = models.CharField(max_length=100)
    nr_reactions = models.IntegerField(default=0)
    nr_metabolites = models.IntegerField(default=0)
    nr_enzymes = models.IntegerField(default=0)
    nr_compartment = models.IntegerField(default=0)

    class Meta:
        db_table = "subsystemsvg"


# "Meta-Svgrmation" tables
class NumberOfInteractionPartners(models.Model):
    reaction_component_id = models.ForeignKey('ReactionComponent', db_column='reaction_component')
    first_order = models.FloatField()
    second_order = models.FloatField(null=True)
    third_order = models.FloatField(null=True)
    catalysed_reactions = models.FloatField(default=0.0)

    class Meta:
        db_table = "number_of_interaction_partners"

#
# ?
#

class MetaboliteReaction(object):
    def __init__(self, reaction, role):
        self.reaction_id = reaction.id
        self.enzyme_role = role
        self.reactants = reaction.reactants
        self.products = reaction.products
        self.modifiers = reaction.modifiers

class ConnectedMetabolites(object):
    def __init__(self, enzyme, compartment, reactions):
        self.enzyme = enzyme
        self.compartment = compartment
        self.reactions = reactions

#
# Relationships
#

class GEMAuthor(models.Model):
    model = models.ForeignKey(GEM, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        db_table = "gem_authors"

class GEMReaction(models.Model):
    model = models.ForeignKey(GEM, on_delete=models.CASCADE)
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)

    class Meta:
        db_table = "gem_reactions"

class ReactionReactant(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    reactant = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_reactants"

class ReactionProduct(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    product = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_products"

class ReactionModifier(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    modifier = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_modifiers"

class CurrencyMetabolite(models.Model):
    component = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)

    class Meta:
        db_table = "currency_metabolites"
        unique_together = (('component', 'reaction'),)

class SubsystemReaction(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_reaction"
        unique_together = (('reaction', 'subsystem'),)

class SubsystemMetabolite(models.Model):
    reaction_component = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_metabolite"
        unique_together = (('reaction_component','subsystem'),)

class SubsystemEnzyme(models.Model):
    reaction_component = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_enzyme"
        unique_together = (('reaction_component','subsystem'),)

class ReactionCompartment(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_compartment"
        unique_together = (('reaction', 'compartment'),)

class ReactionComponentCompartment(models.Model):
    component = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)

    class Meta:
        db_table = "reactioncomponent_compartment"
        unique_together = (('component', 'compartment'),)

class ReactionCompartmentSvg(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    compartmentsvg = models.ForeignKey(CompartmentSvg, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_compartmentsvg"
        unique_together = (('reaction','compartmentsvg'),)

class ReactionComponentCompartmentSvg(models.Model):
    component = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    compartmentsvg = models.ForeignKey(CompartmentSvg, on_delete=models.CASCADE)

    class Meta:
        db_table = "reactioncomponent_compartmentsvg"
        unique_together = (('component','compartmentsvg'),)

#
# From tiles db
#
class TileReactionComponent(models.Model):
    reaction_component_id = models.CharField(max_length=20, primary_key=True)
    tile_name = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = "tile_reactioncomponents"

class TileSubsystem(models.Model):
    subsystem = models.ForeignKey(Subsystem)
    subsystem_name = models.CharField(max_length=200)
    compartmentsvg = models.ForeignKey(CompartmentSvg)
    compartment_name = models.CharField(max_length=125)
    x_top_left = models.IntegerField()
    y_top_left = models.IntegerField()
    x_bottom_right = models.IntegerField()
    y_bottom_right = models.IntegerField()
    reaction_count = models.IntegerField()
    is_main = models.BooleanField(default=False)

    class Meta:
        db_table = "tile_subsystems"
        unique_together = (('subsystem', 'compartment_name'),)
#create table tile_subsystems(id bigserial primary key, subsystem_id integer not null, subsystem_name varchar(200), compartment_name varchar(125), x_top_left integer, y_top_left integer, x_bottom_right integer, y_bottom_right integer, reaction_count integer, is_main boolean);
#insert into tile_subsystems values(4, 38, 'Tricarboxylic acid cycle and glyoxylate/dicarboxylate metabolism', 'm', 12800, 4600, 16800, 9000);

##########################################################################################################################
##########################################################################################################################