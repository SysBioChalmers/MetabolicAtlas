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

class ReactionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Reaction
        fields = ('id', 'name', 'sbo_id', 'equation', 'ec', 'lower_bound', 'upper_bound', 'objective_coefficient',
            'reactants', 'products', 'modifiers')

class ReactionComponentSerializer(serializers.ModelSerializer):

    compartment = serializers.StringRelatedField()
    
    class Meta:
        model = ReactionComponent
        fields = ('id', 'short_name', 'long_name', 'component_type', 'organism', 'formula', 'compartment')

class CurrencyMetaboliteSerializer(serializers.ModelSerializer):

    compartment = serializers.StringRelatedField()
    
    class Meta:
        model = CurrencyMetabolite
        fields = ('reaction_id')

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

