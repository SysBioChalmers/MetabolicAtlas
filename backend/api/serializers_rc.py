from rest_framework import serializers
import api.models as APImodels
from django.db import models
import re

import logging



class MetaboliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Metabolite
        fields = ('mass', 'kegg', 'charge', 'chebi', 'inchi', 'hmdb_description', 'hmdb_link', 'hmdb_function', 'pubchem_link')

class MetaboliteSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Metabolite
        fields = ('kegg', 'hmdb', 'hmdb_name', 'mass')

class EnzymeSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Enzyme
        fields = ('function', 'catalytic_activity', 'ensembl_link', 'uniprot_acc', 'ncbi')

class EnzymeSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Enzyme
        fields = ('uniprot_acc',)

# ================================================================================

# common serializers, map the name of the db column, should not be serve by swagger queries

class ReactionComponentBasicSerializer(serializers.ModelSerializer):
    compartment = serializers.SerializerMethodField('read_compartment')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'full_name', 'aliases', 'formula', 'compartment')

    def read_compartment(self, model):
        return model.compartment_str


class ReactionComponentLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'full_name')


class ReactionComponentSerializer(ReactionComponentBasicSerializer):
    class Meta(ReactionComponentBasicSerializer.Meta): 
        model = APImodels.ReactionComponent
        fields = ReactionComponentBasicSerializer.Meta.fields + \
            ('is_currency', 'alt_name1', 'alt_name2', 'external_id1', 'external_id2', 'external_id3', 'external_id4',)


class EnzymeReactionComponentSerializer(ReactionComponentSerializer):
    function1 = serializers.SerializerMethodField('read_function1')
    function2 = serializers.SerializerMethodField('read_function2')
    ec =  serializers.SerializerMethodField('read_ec')
    catalytic_activity = serializers.SerializerMethodField('read_catalytic_activity')
    cofactor = serializers.SerializerMethodField('read_cofactor')
    name_link = serializers.SerializerMethodField('read_name_link')
    external_link1 = serializers.SerializerMethodField('read_external_link1')
    external_link2 = serializers.SerializerMethodField('read_external_link2')
    external_link3 = serializers.SerializerMethodField('read_external_link3')
    external_link4 = serializers.SerializerMethodField('read_external_link4')

    class Meta(ReactionComponentSerializer.Meta): 
        model = APImodels.ReactionComponent
        fields = ReactionComponentSerializer.Meta.fields + \
            ('function1', 'function2', 'ec', 'catalytic_activity', 'cofactor', 'name_link', 'external_link1', 'external_link2', 'external_link3', 'external_link4',)

    def read_function1(self, model):
        return model.enzyme.function1 if hasattr(model, 'enzyme') else None

    def read_function2(self, model):
        return model.enzyme.function2 if hasattr(model, 'enzyme') else None

    def read_ec(self, model):
        return model.enzyme.ec if hasattr(model, 'enzyme') else None

    def read_catalytic_activity(self, model):
        return model.enzyme.catalytic_activity if hasattr(model, 'enzyme') else None

    def read_cofactor(self, model):
        return model.enzyme.cofactor if hasattr(model, 'enzyme') else None

    def read_name_link(self, model):
        return model.enzyme.name_link if hasattr(model, 'enzyme') else None

    def read_external_link1(self, model):
        return model.enzyme.external_link1 if hasattr(model, 'enzyme') else None

    def read_external_link2(self, model):
        return model.enzyme.external_link2 if hasattr(model, 'enzyme') else None

    def read_external_link3(self, model):
        return model.enzyme.external_link3 if hasattr(model, 'enzyme') else None

    def read_external_link4(self, model):
        return model.enzyme.external_link4 if hasattr(model, 'enzyme') else None


class MetaboliteReactionComponentSerializer(ReactionComponentSerializer):
    description = serializers.SerializerMethodField('read_description')
    function1 = serializers.SerializerMethodField('read_function1')
    function2 = serializers.SerializerMethodField('read_function2')
    charge = serializers.SerializerMethodField('read_charge')
    mass =  serializers.SerializerMethodField('read_mass')
    mass_avg =  serializers.SerializerMethodField('read_mass_avg')
    inchi =  serializers.SerializerMethodField('read_inchi')
    name_link =  serializers.SerializerMethodField('read_name_link')
    external_link1 = serializers.SerializerMethodField('read_external_link1')
    external_link2 = serializers.SerializerMethodField('read_external_link2')
    external_link3 = serializers.SerializerMethodField('read_external_link3')
    external_link4 = serializers.SerializerMethodField('read_external_link4')

    class Meta(ReactionComponentSerializer.Meta):
        model = APImodels.ReactionComponent
        fields = ReactionComponentSerializer.Meta.fields + \
            ('description', 'function1', 'function2',  'charge', 'mass', 'mass_avg', 'inchi', 'name_link', 'external_link1', 'external_link2', 'external_link3', 'external_link4',)

    def read_description(self, model):
        return model.metabolite.description if hasattr(model, 'metabolite') else None

    def read_function1(self, model):
        return model.metabolite.function1 if hasattr(model, 'metabolite') else None

    def read_function2(self, model):
        return model.metabolite.function2 if hasattr(model, 'metabolite') else None

    def read_charge(self, model):
        return model.metabolite.charge if hasattr(model, 'metabolite') else None

    def read_mass(self, model):
        return model.metabolite.mass if hasattr(model, 'metabolite') else None

    def read_mass_avg(self, model):
        return model.metabolite.mass_avg if hasattr(model, 'metabolite') else None

    def read_inchi(self, model):
        return model.metabolite.inchi if hasattr(model, 'metabolite') else None

    def read_name_link(self, model):
        return model.metabolite.name_link if hasattr(model, 'metabolite') else None

    def read_external_link1(self, model):
        return model.metabolite.external_link1 if hasattr(model, 'metabolite') else None

    def read_external_link2(self, model):
        return model.metabolite.external_link2 if hasattr(model, 'metabolite') else None

    def read_external_link3(self, model):
        return model.metabolite.external_link3 if hasattr(model, 'metabolite') else None

    def read_external_link4(self, model):
        return model.metabolite.external_link4 if hasattr(model, 'metabolite') else None

# =====================================================================================

# custom serializers for HMR

class HmrEnzymeReactionComponentLiteSerializer(serializers.ModelSerializer):
    gene_name = serializers.SerializerMethodField('read_gene_name')
    short_name = serializers.SerializerMethodField('read_short_name')
    gene_synonyms = serializers.SerializerMethodField('read_gene_synonyms')
    ec =  serializers.SerializerMethodField('read_ec')
    uniprot_id = serializers.SerializerMethodField('read_uniprot')
    ncbi_id = serializers.SerializerMethodField('read_ncbi')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'gene_name', 'short_name', 'gene_synonyms', 'ec', 'uniprot_id', 'ncbi_id',)

    def read_gene_name(self, model):
        return model.name if model.name else None

    def read_short_name(self, model):
        return model.alt_name1

    def read_gene_synonyms(self, model):
        return model.aliases

    def read_ec(self, model):
        return model.enzyme.ec if hasattr(model, 'enzyme') else None

    def read_uniprot(self, model):
        return model.external_id1

    def read_ncbi(self, model):
        return model.external_id2


class HmrEnzymeReactionComponentSerializer(serializers.ModelSerializer):
    gene_name = serializers.SerializerMethodField('read_gene_name')
    prot_name = serializers.SerializerMethodField('read_prot_name')
    gene_synonyms = serializers.SerializerMethodField('read_gene_synonyms')
    function =  serializers.SerializerMethodField('read_function')
    ec =  serializers.SerializerMethodField('read_ec')
    catalytic_activity =  serializers.SerializerMethodField('read_catalytic_activity')
    cofactor = serializers.SerializerMethodField('read_cofactor')
    uniprot_id = serializers.SerializerMethodField('read_uniprot')
    uniprot_link =  serializers.SerializerMethodField('read_uniprot_link')
    ncbi_id = serializers.SerializerMethodField('read_ncbi')
    ncbi_link =  serializers.SerializerMethodField('read_ncbi_link')
    ensembl_link =  serializers.SerializerMethodField('read_ensembl_link')
    name_link =  serializers.SerializerMethodField('read_name_link')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'gene_name', 'prot_name', 'gene_synonyms') + \
        ('function', 'ec', 'catalytic_activity', 'cofactor') + \
        ('uniprot_id', 'uniprot_link', 'ncbi_id', 'ncbi_link', 'ensembl_link', 'name_link')

    def read_gene_name(self, model):
        return model.name if model.name else None

    def read_prot_name(self, model):
        return model.alt_name1

    def read_gene_synonyms(self, model):
        return model.aliases

    def read_function(self, model):
        return model.enzyme.function1 if hasattr(model, 'enzyme') else None

    def read_ec(self, model):
        return model.enzyme.ec if hasattr(model, 'enzyme') else None

    def read_catalytic_activity(self, model):
        return model.enzyme.catalytic_activity if hasattr(model, 'enzyme') else None

    def read_cofactor(self, model):
        return model.enzyme.cofactor if hasattr(model, 'enzyme') else None

    def read_uniprot(self, model):
        return model.external_id1

    def read_uniprot_link(self, model):
        return model.enzyme.external_link1 if hasattr(model, 'enzyme') else None

    def read_ncbi(self, model):
        return model.external_id2

    def read_ncbi_link(self, model):
        return model.enzyme.external_link2 if hasattr(model, 'enzyme') else None

    def read_ensembl_link(self, model):
        return model.enzyme.name_link if hasattr(model, 'enzyme') else None

    def read_name_link(self, model):
        return model.enzyme.name_link if hasattr(model, 'enzyme') else None


class HmrEnzymeReactionComponentInteractionPartnerSerializer(serializers.ModelSerializer):
    gene_name = serializers.SerializerMethodField('read_gene_name')
    function =  serializers.SerializerMethodField('read_function')
    catalytic_activity = serializers.SerializerMethodField('read_catalytic_activity')
    compartment = serializers.SerializerMethodField('read_compartment')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'gene_name', 'function', 'catalytic_activity', 'compartment')

    def read_gene_name(self, model):
        return model.name if model.name else None

    def read_function(self, model):
        return model.enzyme.function1 if hasattr(model, 'enzyme') else None

    def read_catalytic_activity(self, model):
        return model.enzyme.catalytic_activity if hasattr(model, 'enzyme') else None

    def read_compartment(self, model):
        return model.compartment_str


# -----------------------------------------------------------------------------------------------------


class HmrMetaboliteReactionComponentLiteSerializer(serializers.ModelSerializer):
    model_name = serializers.SerializerMethodField('read_model_name')
    aliases = serializers.SerializerMethodField('read_aliases')
    inchi =  serializers.SerializerMethodField('read_inchi')
    hmdb_id =  serializers.SerializerMethodField('read_hmdb')
    chebi_id = serializers.SerializerMethodField('read_chebi')
    mnxref_id = serializers.SerializerMethodField('read_mnxref')
    compartment = serializers.SerializerMethodField('read_compartment')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'model_name', 'aliases', 'inchi', 'hmdb_id', 'chebi_id', 'mnxref_id', 'compartment',  'is_currency')

    def read_model_name(self, model):
        return model.alt_name1

    def read_aliases(self, model):
        return model.aliases

    def read_inchi(self, model):
        return model.metabolite.inchi if hasattr(model, 'metabolite') else None

    def read_hmdb(self, model):
        return model.external_id1

    def read_chebi(self, model):
        return model.external_id2

    def read_mnxref(self, model):
        return model.external_id3

    def read_compartment(self, model):
        return model.compartment_str


class HmrMetaboliteReactionComponentSerializer(serializers.ModelSerializer):
    alt_name = serializers.SerializerMethodField('read_alt_name')
    aliases = serializers.SerializerMethodField('read_aliases')
    description = serializers.SerializerMethodField('read_description')
    function = serializers.SerializerMethodField('read_function')
    formula = serializers.SerializerMethodField('read_formula')
    charge = serializers.SerializerMethodField('read_charge')
    mass =  serializers.SerializerMethodField('read_mass')
    mass_avg =  serializers.SerializerMethodField('read_mass_avg')
    inchi =  serializers.SerializerMethodField('read_inchi')
    hmdb_id =  serializers.SerializerMethodField('read_hmdb')
    hmdb_link = serializers.SerializerMethodField('read_hmdb_link')
    chebi_id = serializers.SerializerMethodField('read_chebi')
    chebi_link = serializers.SerializerMethodField('read_chebi_link')
    mnxref_id = serializers.SerializerMethodField('read_mnxref')
    mnxref_link = serializers.SerializerMethodField('read_mnxref_link')
    compartment = serializers.SerializerMethodField('read_compartment')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'alt_name', 'aliases') + \
        ('description', 'function', 'formula', 'charge', 'mass', 'mass_avg', 'inchi') + \
        ('hmdb_id', 'hmdb_link', 'chebi_id', 'chebi_link', 'mnxref_id', 'mnxref_link', 'compartment')

    def read_alt_name(self, model):
        return model.alt_name1

    def read_aliases(self, model):
        return model.aliases

    def read_description(self, model):
        return model.metabolite.description if hasattr(model, 'metabolite') else None

    def read_function(self, model):
        return model.metabolite.function1 if hasattr(model, 'metabolite') else None

    def read_formula(self, model):
        return model.formula

    def read_charge(self, model):
        return model.metabolite.charge if hasattr(model, 'metabolite') else None

    def read_mass(self, model):
        return model.metabolite.mass if hasattr(model, 'metabolite') else None

    def read_mass_avg(self, model):
        return model.metabolite.mass_avg if hasattr(model, 'metabolite') else None

    def read_inchi(self, model):
        return model.metabolite.inchi if hasattr(model, 'metabolite') else None

    def read_hmdb(self, model):
        return model.external_id1

    def read_hmdb_link(self, model):
        return model.metabolite.external_link1 if hasattr(model, 'metabolite') else None

    def read_chebi(self, model):
        return model.external_id2

    def read_chebi_link(self, model):
        return model.metabolite.external_link2 if hasattr(model, 'metabolite') else None

    def read_mnxref(self, model):
        return model.external_id3

    def read_mnxref_link(self, model):
        return model.metabolite.external_link3 if hasattr(model, 'metabolite') else None

    def read_compartment(self, model):
        return model.compartment_str


class HmrMetaboliteReactionComponentInteractionPartnerSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField('read_description')
    function = serializers.SerializerMethodField('read_function')
    compartment = serializers.SerializerMethodField('read_compartment')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'description', 'function', 'compartment')

    def read_description(self, model):
        return model.metabolite.description if hasattr(model, 'metabolite') else None

    def read_function(self, model):
        return model.metabolite.function1 if hasattr(model, 'metabolite') else None

    def read_compartment(self, model):
        return model.compartment_str


# ==========================================================================================

# custom serializers for yeast

# ==========================================================================================

# custom serializers for the GEM browser Tiles
class GemBrowserTileReactionSerializer(serializers.ModelSerializer):
    compartment_count = serializers.SerializerMethodField('read_compartment_count')
    subsystem_count = serializers.SerializerMethodField('read_subsystem_count')
    enzymes_count = serializers.SerializerMethodField('read_enzymes_count')

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'equation_wname', 'is_reversible', 'subsystem_count', 'compartment_count', 'enzymes_count')

    def read_compartment_count(self, model):
        return len(re.compile(" => | + ").split(model.compartment))

    def read_subsystem_count(self, model):
        return model.subsystem.count()

    def read_enzymes_count(self, model):
        return model.modifiers.count()


class GemBrowserTileMetaboliteSerializer(serializers.ModelSerializer):
    compartment = serializers.SerializerMethodField('read_compartment')
    reaction_count = serializers.SerializerMethodField('read_reaction_count')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'formula', 'compartment', 'reaction_count')

    def read_compartment(self, model):
        return model.compartment_str

    def read_reaction_count(self, model):
        return model.reactions_as_reactant.count() + model.reactions_as_product.count()


class GemBrowserTileEnzymeSerializer(serializers.ModelSerializer):
    compartment_count = serializers.SerializerMethodField('read_compartment')
    subsystem_count = serializers.SerializerMethodField('read_subsystem')
    reaction_count = serializers.SerializerMethodField('read_reaction_count')

    class Meta:
        model = APImodels.ReactionComponent
        fields = ('id', 'name', 'reaction_count', 'compartment_count', 'subsystem_count')

    def read_compartment(self, model):
        return model.compartments.count()

    def read_subsystem(self, model):
        return model.subsystem_enzyme.count()

    def read_reaction_count(self, model):
        return model.reactions_as_modifier.count()