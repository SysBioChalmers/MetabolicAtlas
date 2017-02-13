from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from api.models import MetabolicModel, Author
from api.serializers import MetabolicModelSerializer, AuthorSerializer

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def model_list(request):
    models = MetabolicModel.objects.all()
    serializer = MetabolicModelSerializer(models, many=True)
    return JSONResponse(serializer.data)

@csrf_exempt
def author_list(request):
    author = Author.objects.all()
    serializer = AuthorSerializer(author, many=True)
    return JSONResponse(serializer.data)
