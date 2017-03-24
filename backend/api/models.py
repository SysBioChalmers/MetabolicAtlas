from django.db import models

#
# Models
#

class MetabolicModel(models.Model):
    short_name = models.CharField(max_length=255, blank=False)
    name = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return "<MetabolicModel: {0}>".format(self.short_name)

    class Meta:
        db_table = "metabolic_model"

class Author(models.Model):
    given_name = models.CharField(max_length=255, blank=False)
    family_name = models.CharField(max_length=255, blank=False)
    email = models.CharField(max_length=255, blank=False)
    organization = models.CharField(max_length=255, blank=False)
    models = models.ManyToManyField(MetabolicModel, related_name='authors', through='ModelAuthor')

    def __str__(self):
        return "<Author: {0} {1}>".format(self.given_name, self.family_name)

    class Meta:
        db_table = "author"

class Reaction(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    sbo_id = models.CharField(max_length=255)
    equation = models.TextField(blank=False)
    ec = models.CharField(max_length=255, null=True)
    lower_bound = models.FloatField()
    upper_bound = models.FloatField()
    objective_coefficient = models.FloatField()

    models = models.ManyToManyField(MetabolicModel, related_name='reactions', through='ModelReaction')

    #currency_metabolites = models.ManyToManyField(Reaction,
    #    related_name='reaction_component', through='CurrencyMetabolite')

    def __str__(self):
        return "<Reaction: {0}>".format(self.id)

    class Meta:
        db_table = "reaction"

class ReactionComponent(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    short_name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)
    component_type = models.CharField(max_length=50, db_index=True)
    organism = models.CharField(max_length=255)
    formula = models.CharField(max_length=255, null=True) # only metabolites have this!
    compartment = models.ForeignKey('Compartment', db_column='compartment', blank=True)

    reactions_as_reactant = models.ManyToManyField(Reaction, related_name='reactants', through='ReactionReactant')
    reactions_as_product = models.ManyToManyField(Reaction, related_name='products', through='ReactionProduct')
    reactions_as_modifier = models.ManyToManyField(Reaction, related_name='modifiers', through='ReactionModifier')
    currency_metabolites = models.ManyToManyField(Reaction, related_name='currency_metabolites', through='CurrencyMetabolite')

    def __str__(self):
        return "<ReactionComponent: {0}>".format(self.id)

    class Meta:
        db_table = "reaction_component"

# TODO: add this table in db
class ReactionComponentAnnotation(models.Model):
    pass

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
    transcript_id = models.CharField(max_length=35)
    tissue = models.CharField(max_length=100)
    cell_type = models.CharField(max_length=255)
    level = models.CharField(max_length=30)
    expression_type = models.CharField(max_length=35)
    reliability = models.CharField(max_length=35)
    source = models.CharField(max_length=45)

    class Meta:
        db_table = "expression_data"
        unique_together = (('id', 'gene_id', 'transcript_id', 'tissue', 'cell_type', 'expression_type'),)

class Metabolite(models.Model):
    hmdb = models.CharField(max_length=10)
    formula = models.CharField(max_length=50)
    charge = models.FloatField()
    mass = models.FloatField()
    mass_avg = models.FloatField()
    kegg = models.CharField(max_length=50)
    chebi = models.CharField(max_length=50)
    inchi = models.CharField(max_length=255)
    bigg = models.CharField(max_length=55)
    # relationship: components

    class Meta:
        db_table = "metabolites"

class Enzyme(models.Model):
    uniprot_acc = models.CharField(max_length=35, unique=True)
    protein_name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=75)
    ec = models.CharField(max_length=100)
    kegg = models.CharField(max_length=125)
    function = models.CharField(max_length=6000)
    catalytic_activity = models.CharField(max_length=700)
    # relationship: components

    class Meta:
        db_table = "enzymes"

class MetaboliteReaction(object):
    def __init__(self, reaction, role):
        self.reaction_id = reaction.id
        self.enzyme_role = role
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

#
# Relationships
#

class ModelAuthor(models.Model):
    model = models.ForeignKey(MetabolicModel, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        db_table = "model_authors"

class ModelReaction(models.Model):
    model = models.ForeignKey(MetabolicModel, on_delete=models.CASCADE)
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)

    class Meta:
        db_table = "model_reactions"

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
