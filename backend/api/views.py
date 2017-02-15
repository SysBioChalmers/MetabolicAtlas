from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from api.models import MetabolicModel, Author
from api.serializers import *

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@api_view()
def model_list(request):
    models = MetabolicModel.objects.all()
    serializer = MetabolicModelSerializer(models, many=True)
    return JSONResponse(serializer.data)

@api_view()
def get_model(request, id):
    try:
        model = MetabolicModel.objects.get(id=id)
    except MetabolicModel.DoesNotExist:
        return HttpResponse(status=404)

    serializer = MetabolicModelSerializer(model)
    return JSONResponse(serializer.data)

@api_view()
def author_list(request):
    authors = Author.objects.all()
    serializer = AuthorSerializer(authors, many=True)
    return JSONResponse(serializer.data)

@api_view()
def get_author(request, id):
    try:
        author = Author.objects.get(id=id)
    except Author.DoesNotExist:
        return HttpResponse(status=404)

    serializer = AuthorSerializer(author)
    return JSONResponse(serializer.data)

@api_view()
def reaction_list(request):
    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))
    reactions = Reaction.objects.all()[offset:(offset+limit)]
    serializer = ReactionSerializer(reactions, many=True)
    return JSONResponse(serializer.data)

@api_view()
def get_reaction(request, id):
    try:
        reaction = Reaction.objects.get(id=id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionSerializer(reaction)
    return JSONResponse(serializer.data)


