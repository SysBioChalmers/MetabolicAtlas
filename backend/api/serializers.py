from rest_framework import serializers
from api.models import MetabolicModel, Author

class MetabolicModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = MetabolicModel
        fields = ('id', 'short_name', 'name')

class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = ('id', 'given_name', 'family_name', 'email', 'organization')

