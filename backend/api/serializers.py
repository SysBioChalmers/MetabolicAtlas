from rest_framework import serializers
from api.models import *

class MetabolicModelSerializer(serializers.ModelSerializer):
    authors = serializers.StringRelatedField(many=True)

    class Meta:
        model = MetabolicModel
        fields = ('id', 'short_name', 'name', 'authors')

class AuthorSerializer(serializers.ModelSerializer):
    models = serializers.StringRelatedField(many=True)

    class Meta:
        model = Author
        fields = ('id', 'given_name', 'family_name', 'email', 'organization', 'models')

class MetaboliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metabolite
        fields = ('mass', 'kegg', 'charge', 'chebi', 'inchi', 'hmdb_description', 'hmdb_link', 'hmdb_function', 'pubchem_link')

class MetaboliteSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metabolite
        fields = ('kegg', 'hmdb', 'hmdb_name')

class EnzymeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enzyme
        fields = ('function', 'catalytic_activity', 'uniprot_link', 'ensembl_link')

class EnzymeSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enzyme
        fields = ('uniprot_acc',)

class ReactionComponentSerializer(serializers.ModelSerializer):
    compartment = serializers.StringRelatedField()
    metabolite = MetaboliteSerializer(read_only=True)
    enzyme = EnzymeSerializer(read_only=True)
    
    class Meta:
        model = ReactionComponent
        fields = ('id', 'short_name', 'long_name', 'component_type', 'organism', 'formula', 'compartment', 'metabolite', 'enzyme', 'currency_metabolites')

class ReactionComponentSearchSerializer(serializers.ModelSerializer):
    compartment = serializers.StringRelatedField()
    metabolite = MetaboliteSearchSerializer(read_only=True)
    enzyme = EnzymeSearchSerializer(read_only=True)
    
    class Meta:
        model = ReactionComponent
        fields = ('id', 'short_name', 'long_name', 'component_type', 'organism', 'formula', 'compartment', 'metabolite', 'enzyme')

class ReactionSerializer(serializers.ModelSerializer):
    reactants = ReactionComponentSerializer(many=True)
    products = ReactionComponentSerializer(many=True)
    modifiers = ReactionComponentSerializer(many=True)
    class Meta:
        model = Reaction
        fields = ('id', 'name', 'sbo_id', 'equation', 'ec', 'lower_bound', 'upper_bound', 'objective_coefficient',
            'reactants', 'products', 'modifiers', 'subsystem')


# This is a helper class to determine if a component is a currency metabolite
class CurrencyMetaboliteReactionComponent(object):
    def __init__(self, reaction_component, reaction_id):
        self.reaction_component = reaction_component
        self.reaction_id = reaction_id
        self.is_currency_metabolite = self.__is_currency_metabolite__()

    def __is_currency_metabolite__(self):
        for r in self.reaction_component.currency_metabolites.all():
            if r.id == self.reaction_id:
                return True
        return False

class CurrencyMetaboliteReactionComponentSerializer(serializers.Serializer):
    reaction_component = ReactionComponentSerializer(read_only=True)
    is_currency_metabolite = serializers.BooleanField()

class CurrencyMetaboliteSerializer(serializers.ModelSerializer):
    compartment = serializers.StringRelatedField()
    
    class Meta:
        model = CurrencyMetabolite
        fields = ('reaction_id', 'compartment')

class ExpressionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpressionData
        fields = ('gene_id', 'gene_name', 'transcript_id', 'tissue', 'expression_type', 'level', 'cell_type', 'reliability', 'source')

class InteractionPartnerSerializer(serializers.ModelSerializer):
    modifiers = ReactionComponentSerializer(many=True, read_only=True)
    products = ReactionComponentSerializer(many=True, read_only=True)
    reactants = ReactionComponentSerializer(many=True, read_only=True)
    currency_metabolites = CurrencyMetaboliteSerializer(many=True, read_only=True)

    class Meta:
        model = ReactionComponent
        fields = ('id', 'modifiers', 'products', 'reactants', 'currency_metabolites')

class MetaboliteReactionSerializer(serializers.Serializer):
    reaction_id = serializers.CharField()
    enzyme_role = serializers.CharField()
    reaction_subsystem = serializers.CharField()
    reactants = ReactionComponentSerializer(many=True, read_only=True)
    products = ReactionComponentSerializer(many=True, read_only=True)
    modifiers = ReactionComponentSerializer(many=True, read_only=True)


class ConnectedMetabolitesSerializer(serializers.Serializer):
    id = serializers.CharField()
    short_name = serializers.CharField()
    long_name = serializers.CharField()
    compartment = serializers.CharField()
    reactions = MetaboliteReactionSerializer(many=True)
    expressions = ExpressionDataSerializer(many=True)
    uniprot_link = serializers.CharField()
    ensembl_link = serializers.CharField()

# =======================================================================================

class GemFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GemFile
        fields = ('path', 'format')

class GemReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GemReference
        fields = ('title', 'link', 'pubmed')

class GemGroupSerializer(serializers.ModelSerializer):
    reference = GemReferenceSerializer(many=True, read_only=True)
    class Meta:
        model = GemGroup
        fields = ('name', 'description', 'reference')

class GemSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GemSample
        fields = ('organism', 'organ_system', 'tissue', 'cell_line', 'cell_type')


class GemReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GemReference
        fields = ('title', 'link', 'pubmed')

class GemSerializer(serializers.ModelSerializer):
    group = GemGroupSerializer()
    sample = GemSampleSerializer()
    files = GemFileSerializer(many=True, read_only=True)
    reference = serializers.SerializerMethodField('get_gem_reference')

    def get_gem_reference(self, model):
        if model.reference:
            return model.reference
        else:
            return model.group.reference[0]

    class Meta:
        model = Gem
        fields = ('id', 'group', 'sample', 'label', 'reaction_count', 'metabolite_count', 'enzyme_count', 'files', 'reference', 'maintained', 'year')


class GemListSerializer(serializers.ModelSerializer):
    group_name = serializers.SerializerMethodField('get_gem_group_name')
    sample = GemSampleSerializer()

    def get_gem_group_name(self, model):
        gg = GemGroup.objects.get(id=model.group.id)
        return gg.name

    class Meta:
        model = Gem
        fields = ('group_name', 'sample', 'label', 'reaction_count', 'metabolite_count', 'enzyme_count', 'maintained', 'year')