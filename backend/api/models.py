from django.db import models
from django.db.models.fields import Field
from django.db.models import Lookup

@Field.register_lookup
class ILike(Lookup):
    lookup_name = 'ilike'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        # The key word ILIKE make the match case-insensitive according to the active locale.
        # This is not in the SQL standard but is a PostgreSQL extension.
        return '%s ILIKE %s' % (lhs, rhs), params


class GEModelReference(models.Model):
    title = models.TextField()
    link = models.TextField()
    pubmed = models.CharField(max_length=20, unique=True, null=True)
    year = models.CharField(max_length=4)

    class Meta:
        db_table = "gemodel_reference"


class GEModelSet(models.Model):
    CATEGORY = (
        ('Species', 'Species'),
        ('Community', 'Community'),
        ('Collection', 'Collection'),
    )
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True)
    reference = models.ManyToManyField(GEModelReference, related_name='gemodelset_references')

    class Meta:
        db_table = "gemodel_set"


class GEModelSample(models.Model):
    organism = models.CharField(max_length=200)
    organ_system = models.CharField(max_length=200, null=True)
    tissue = models.CharField(max_length=200, null=True)
    cell_type = models.CharField(max_length=200, null=True)
    cell_line = models.CharField(max_length=200, null=True)

    unique_together = (('organism', 'organ_system', 'tissue', 'cell_type', 'cell_line'),)

    class Meta:
        db_table = "gemodel_sample"


class GEModelFile(models.Model):
    path = models.CharField(max_length=500, unique=True)
    format = models.CharField(max_length=50)

    class Meta:
        db_table = "gemodel_file"


class GEModel(models.Model):
    gemodelset = models.ForeignKey(GEModelSet, on_delete=models.CASCADE)
    sample = models.ForeignKey(GEModelSample, on_delete=models.CASCADE)
    description = models.TextField(null=True)
    label = models.CharField(max_length=200, null=True)
    reaction_count = models.IntegerField(default=0)
    metabolite_count = models.IntegerField(default=0)
    enzyme_count = models.IntegerField(default=0)
    files = models.ManyToManyField(GEModelFile, related_name='gemodel_files')
    maintained = models.BooleanField(default=False)
    ref = models.ManyToManyField(GEModelReference, related_name='gemodels_refs', blank=True)
    last_update = models.DateField(null=True)
    repo_name = models.CharField(max_length=200, null=True)

    def save(self, *args, **kwargs):
        if not self.gemodelset:
            raise AttributeError("Model set must be specified")
        if not self.sample:
            raise AttributeError("Model sample must be specified")
        if not self.reaction_count and not self.metabolite_count and not self.enzyme_count:
            raise AttributeError("component count cannot be all 0")
        super(GEModel, self).save(*args, **kwargs)

    class Meta:
        db_table = "gemodel"


##########################################################################################################################
##########################################################################################################################
# part of Gems database

class Author(models.Model):
    given_name = models.CharField(max_length=255, blank=False)
    family_name = models.CharField(max_length=255, blank=False)
    email = models.CharField(max_length=255, blank=False)
    organization = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return "<Author: {0} {1}>".format(self.given_name, self.family_name)

    class Meta:
        db_table = "author"

class GEM(models.Model):
    name = models.CharField(max_length=255, blank=False)
    short_name = models.CharField(max_length=255, blank=False)
    database_name = models.CharField(max_length=255, blank=False, unique=True)
    publication =  models.OneToOneField( # only one main paper per model
            'GEModelReference',
            related_name='publication',
            db_column='publication',
            on_delete=models.SET_NULL, null=True)
    ensembl_version = models.CharField(max_length=50, null=True)
    ensembl_archive_url = models.CharField(max_length=50, null=True)
    authors = models.ManyToManyField(Author, related_name='authors', through='GEMAuthor')
    model = models.OneToOneField(
            'GEModel',
            related_name='model',
            db_column='model',
            on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "<GEM: {0} {1} {2}>".format(self.name, self.short_name, self.database_name)

    class Meta:
        db_table = "gem"


class GEMAuthor(models.Model):
    model = models.ForeignKey(GEM, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        db_table = "gem_author"

##########################################################################################################################
##########################################################################################################################

#
# Full Models
#

class Reaction(models.Model):
    id = models.CharField(max_length=50, primary_key=True) # ID in the SBML/YAML model
    name = models.CharField(max_length=50)
    sbo_id = models.CharField(max_length=50)
    equation = models.TextField(blank=False) # string or/and with metabolite ID (should be meta model ID, e.g M_m0125c)
    equation_wname = models.TextField(blank=False)
    ec = models.CharField(max_length=255, null=True)
    lower_bound = models.FloatField()
    upper_bound = models.FloatField()
    objective_coefficient = models.FloatField(null=True)
    gene_rule = models.TextField(null=True) # string or/and with gene ID (can be any unique gene ID)
    gene_rule_wname = models.TextField(null=True) # string or/and with gene name
    subsystem_str = models.CharField(max_length=1000)
    subsystem = models.ManyToManyField('Subsystem', related_name='subsystems', through='SubsystemReaction')
    compartment = models.CharField(max_length=255)
    is_transport = models.BooleanField(default=False)
    is_reversible = models.BooleanField(default=False)

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



# corresponds to either metabolite or enzyme, should be Serialized with the proper serializer
class ReactionComponent(models.Model):
    id = models.CharField(max_length=50, primary_key=True) # ID in the SBML/YAML model
    name = models.CharField(max_length=255)  # gene name for enzyme, or metabolite name with compartment code
    alt_name1 = models.CharField(max_length=255, null=True)  # can be ORF ID in case of yeast, proteine name, metabolite short_name etc
    alt_name2 = models.CharField(max_length=255, null=True)  # can be ORF ID in case of yeast, proteine name, metabolite short_name etc
    aliases = models.CharField(max_length=2000, null=True)  # alias of gene name (including gene short name) or alias of metabolite name, semi-colon separated values
    external_id1 = models.CharField(max_length=50, null=True) # e.g. MNXref, HMDB, chebi or kegg or uniprot or ensembl, etc need to be specify in the serializer
    external_id2 = models.CharField(max_length=50, null=True)  # e.g. MNXref, HMDB, chebi or kegg or uniprot or ensembl, etc need to be specify in the serializer
    external_id3 = models.CharField(max_length=50, null=True)  # e.g. MNXref, HMDB, chebi or kegg or uniprot or ensembl, etc need to be specify in the serializer
    external_id4 = models.CharField(max_length=50, null=True)  # e.g. MNXref, HMDB, chebi or kegg or uniprot or ensembl, etc need to be specify in the serializer
    component_type = models.CharField(max_length=1, db_index=True)  # 'm' or 'e' for metabolite or enzyme
    formula = models.CharField(max_length=255, null=True)        # only metabolites have this! should be in metabolite table but will simplify the queries if here
    compartment_str = models.CharField(max_length=255, null=True)
    compartment = models.ForeignKey('Compartment', db_column='compartment', null=True, on_delete=models.CASCADE)
    is_currency = models.BooleanField(default=False) # only for metabolite, should be in metabolite table but will simplify the queries if here

    reactions_as_reactant = models.ManyToManyField(Reaction, related_name='reactants', through='ReactionReactant')
    reactions_as_product = models.ManyToManyField(Reaction, related_name='products', through='ReactionProduct')
    reactions_as_modifier = models.ManyToManyField(Reaction, related_name='modifiers', through='ReactionModifier')

    def __str__(self):
        return "<ReactionComponent: {0}>".format(self.id)

    class Meta:
        db_table = "reaction_component"

'''class HumanReactionComponent(ReactionComponent):
    def __init__(self, *args, **kwargs):
        super(models.Model, self).__init__(self, *args, **kwargs)
        self.gene_name2 = self.name'''

class Metabolite(models.Model):
    rc = models.OneToOneField(
            'ReactionComponent',
            related_name='metabolite',
            db_column='rc',
            on_delete=models.CASCADE)
    description = models.TextField(null=True)
    function1 = models.CharField(max_length=3000, null=True)
    function2 = models.CharField(max_length=3000, null=True)
    charge = models.FloatField(null=True)
    mass = models.FloatField(null=True)
    mass_avg = models.FloatField(null=True)
    inchi = models.CharField(max_length=255, null=True)
    name_link = models.CharField(max_length=255, null=True)
    external_link1 = models.CharField(max_length=255, null=True)
    external_link2 = models.CharField(max_length=255, null=True)
    external_link3 = models.CharField(max_length=255, null=True)
    external_link4 = models.CharField(max_length=255, null=True)


    class Meta:
        db_table = "metabolite"

class Enzyme(models.Model):
    rc = models.OneToOneField('ReactionComponent',
        related_name='enzyme', db_column='rc', on_delete=models.CASCADE)
    function1 = models.CharField(max_length=3000, null=True)
    function2 = models.CharField(max_length=3000, null=True)
    ec = models.CharField(max_length=100, null=True)
    catalytic_activity = models.CharField(max_length=2000, null=True)
    cofactor = models.CharField(max_length=255, null=True)
    name_link = models.CharField(max_length=255, null=True)
    external_link1 = models.CharField(max_length=255, null=True)
    external_link2 = models.CharField(max_length=255, null=True)
    external_link3 = models.CharField(max_length=255, null=True)
    external_link4 = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "enzyme"

'''
class CoFactor(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "cofactor"
'''

class Subsystem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    system = models.CharField(max_length=100)
    external_id = models.CharField(max_length=25, null=True)
    external_link = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=2000, null=True)
    compartment = models.ManyToManyField('Compartment', related_name='s_compartments', through='SubsystemCompartment')
    reaction_count = models.IntegerField(default=0)
    metabolite_count = models.IntegerField(default=0)
    unique_metabolite_count = models.IntegerField(default=0)
    enzyme_count = models.IntegerField(default=0)
    compartment_count = models.IntegerField(default=0)

    class Meta:
        db_table = "subsystem"

class SubsystemSvg(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    subsystem = models.OneToOneField(Subsystem,
        related_name='subsystem', db_column='subsystem', on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50, unique=True)
    filename = models.CharField(max_length=50)
    reaction_count = models.IntegerField(default=0)
    metabolite_count = models.IntegerField(default=0)
    unique_metabolite_count = models.IntegerField(default=0)
    enzyme_count = models.IntegerField(default=0)
    compartment_count = models.IntegerField(default=0)
    min_zoom_level = models.FloatField(default=0)
    max_zoom_level = models.FloatField(default=0)
    node_zoom_level = models.FloatField(default=0)
    label_zoom_level = models.FloatField(default=0)

    class Meta:
        db_table = "subsystemsvg"

class Compartment(models.Model):
    name = models.CharField(max_length=50, unique=True)
    letter_code = models.CharField(max_length=3, unique=True)
    subsystem = models.ManyToManyField('Subsystem', related_name='c_subsystems', through='SubsystemCompartment')
    reaction_count = models.IntegerField(default=0)
    subsystem_count = models.IntegerField(default=0)
    metabolite_count = models.IntegerField(default=0)
    unique_metabolite_count = models.IntegerField(default=0)  # = metabolite_count
    enzyme_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "compartment"

class CompartmentSvg(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    compartment = models.ForeignKey('Compartment', on_delete=models.CASCADE)
    subsystem = models.ManyToManyField('Subsystem', related_name='csvg_subsystems', through='SubsystemCompartmentSvg')
    display_name = models.CharField(max_length=50, unique=True)
    filename = models.CharField(max_length=50)
    letter_code = models.CharField(max_length=3, unique=True)
    reaction_count = models.IntegerField(default=0)
    subsystem_count = models.IntegerField(default=0)
    metabolite_count = models.IntegerField(default=0)
    unique_metabolite_count = models.IntegerField(default=0)
    enzyme_count = models.IntegerField(default=0)
    min_zoom_level = models.FloatField(default=0)
    max_zoom_level = models.FloatField(default=0)
    node_zoom_level = models.FloatField(default=0)
    label_zoom_level = models.FloatField(default=0)

    class Meta:
        db_table = "compartmentsvg"

class NumberOfInteractionPartners(models.Model):
    rc = models.ForeignKey('ReactionComponent', db_column='rc', on_delete=models.CASCADE)
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

'''
class EnzymeCoFactor(models.Model):
    enzyme = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    cofactor = models.ForeignKey(CoFactor, on_delete=models.CASCADE)

    class Meta:
        db_table = "enzyme_cofactor"
'''

class ReactionReactant(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    reactant = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_reactant"

class ReactionProduct(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    product = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_product"

class ReactionModifier(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    modifier = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_modifier"

class CurrencyMetaboliteCompartment(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)

    class Meta:
        db_table = "currency_metabolite_compartment"
        unique_together = (('rc', 'compartment'),)

class SubsystemReaction(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_reaction"
        unique_together = (('reaction', 'subsystem'),)

class SubsystemMetabolite(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_metabolite"
        unique_together = (('rc', 'subsystem'),)

class SubsystemEnzyme(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_enzyme"
        unique_together = (('rc', 'subsystem'),)

class SubsystemCompartment(models.Model):
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_compartment"

class ReactionCompartment(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_compartment"
        unique_together = (('reaction', 'compartment'),)

class ReactionComponentCompartment(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)

    class Meta:
        db_table = "rc_compartment"
        unique_together = (('rc', 'compartment'),)

class ReactionCompartmentSvg(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    compartmentsvg = models.ForeignKey(CompartmentSvg, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_compartmentsvg"
        unique_together = (('reaction', 'compartmentsvg'),)

class ReactionComponentCompartmentSvg(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    compartmentsvg = models.ForeignKey(CompartmentSvg, on_delete=models.CASCADE)

    class Meta:
        db_table = "rc_compartmentsvg"
        unique_together = (('rc', 'compartmentsvg'),)

class ReactionSubsystemSvg(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    subsystemsvg = models.ForeignKey(SubsystemSvg, on_delete=models.CASCADE)

    class Meta:
        db_table = "reaction_subsystemsvg"
        unique_together = (('reaction', 'subsystemsvg'),)

# corresponds to SubsystemEnzyme ans SubsystemMetabolite for subsystem in the model
class ReactionComponentSubsystemSvg(models.Model):
    rc = models.ForeignKey(ReactionComponent, on_delete=models.CASCADE)
    subsystemsvg = models.ForeignKey(SubsystemSvg, on_delete=models.CASCADE)

    class Meta:
        db_table = "rc_subsystemsvg"
        unique_together = (('rc', 'subsystemsvg'),)

# relation subsystem / compartment in SVGs was previously found in TilesSubsystems
class SubsystemCompartmentSvg(models.Model):
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE)
    compartmentsvg = models.ForeignKey(CompartmentSvg, on_delete=models.CASCADE)

    class Meta:
        db_table = "subsystem_compartmentsvg"
        unique_together = (('subsystem', 'compartmentsvg'),)

##########################################################################################################################
##########################################################################################################################


class HpaTissue(models.Model):
    index = models.IntegerField(primary_key=True)
    tissue = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "hpa_tissue"

class HpaEnzymeLevel(models.Model):
    rc = models.OneToOneField(ReactionComponent, on_delete=models.CASCADE, primary_key=True)
    levels = models.CharField(max_length=1000)

    class Meta:
        db_table = "hpa_enzyme_level"
