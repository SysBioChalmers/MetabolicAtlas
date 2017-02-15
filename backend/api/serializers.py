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

