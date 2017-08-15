from django.db import models

#
# From gems db
#
class GEModel(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200, null=True)
    organism = models.CharField(max_length=200, null=True)
    tissue = models.CharField(max_length=200, null=True)
    celltype = models.CharField(max_length=200, null=True)
    cellline = models.CharField(max_length=200, null=True)
    path = models.CharField(max_length=200, null=True)
    maintained = models.CharField(max_length=200, null=True)
    pubmed = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = "gemodels"

#
# From tiles db
#
class Tile(models.Model):
    reaction_component_id = models.CharField(max_length=50, primary_key=True)
    tile_name = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = "tiles"

#
# Extra "annotation" models, such as BTO mappings
#
class TissueOntology(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=95, unique=True)
    definition = models.CharField(max_length=7000, null=True)

    class Meta:
        db_table = "tissue_ontology"

#
# Models
#

class GEM(models.Model):
    short_name = models.CharField(max_length=255, blank=False)
    name = models.CharField(max_length=255, blank=False)
    pmid = models.CharField(max_length=11, blank=False)
    article_title = models.CharField(max_length=255, blank=False)
    ensembl_version = models.CharField(max_length=50, null=True) # keep track of this... for HMR2 make an educated guess!
    ensembl_archive_path = models.CharField(max_length=50, null=True)

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
    compartment = models.CharField(max_length=125)
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

    def __str__(self):
        return self.name

    class Meta:
        db_table = "compartment"

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
    hmdb = models.CharField(max_length=10, null=True)
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
    hmdb_function = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "metabolites"

class Enzyme(models.Model):
    reaction_component = models.OneToOneField('ReactionComponent',
        related_name='enzyme', db_column='reaction_component')
    uniprot_acc = models.CharField(max_length=35)
    protein_name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=75)
    ec = models.CharField(max_length=100, null=True)
    kegg = models.CharField(max_length=125, null=True)
    function = models.CharField(max_length=6000, null=True)
    catalytic_activity = models.CharField(max_length=700, null=True)
    uniprot_link = models.CharField(max_length=255, null=True) # if the UniProt link is not valid, then something is wrong!
    ensembl_link = models.CharField(max_length=255, null=True) # should link to the RIGHT Ensembl version, otherwise leave as null...

    class Meta:
        db_table = "enzymes"


class Subsystem(models.Model):
    name = models.CharField(max_length=100, null=False)
    system = models.CharField(max_length=100, null=False)
    external_id = models.CharField(max_length=25, null=True)
    description = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "subsystems"


# "Meta-information" tables
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
        self.reaction_subsystem = "NEED TO ADD SOMETHING HERE"
        self.reactants = reaction.reactants.filter(component_type='metabolite')
        self.products = reaction.products.filter(component_type='metabolite')
        self.modifiers = reaction.modifiers.filter(component_type='metabolite')

class ConnectedMetabolites(object):
    def __init__(self, enzyme, compartment, reactions, expressions):
        self.id = enzyme.id
        self.short_name = enzyme.short_name
        self.long_name = enzyme.long_name
        self.compartment = compartment
        self.reactions = reactions
        self.expressions = expressions
        self.uniprot_link = enzyme.enzyme.uniprot_link
        self.ensembl_link = enzyme.enzyme.ensembl_link

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

class ReactionSubsystem(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_subsystem"
        unique_together = (('reaction', 'subsystem'),)
