from django.http import HttpResponse
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from itertools import chain
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

@api_view()
def reaction_reactant_list(request, id):
    try:
        reaction = Reaction.objects.get(id=id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(reaction.reactants, many=True)
    return JSONResponse(serializer.data)

@api_view()
def get_reaction_reactant(request, reaction_id, reactant_id):
    try:
        reaction = Reaction.objects.get(id=reaction_id)
        reactant = reaction.reactants.get(id=reactant_id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(reactant)
    return JSONResponse(serializer.data)

@api_view()
def reaction_product_list(request, id):
    try:
        reaction = Reaction.objects.get(id=id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(reaction.products, many=True)
    return JSONResponse(serializer.data)

@api_view()
def get_reaction_product(request, reaction_id, product_id):
    try:
        reaction = Reaction.objects.get(id=reaction_id)
        product = reaction.products.get(id=product_id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(product)
    return JSONResponse(serializer.data)

@api_view()
def reaction_modifier_list(request, id):
    try:
        reaction = Reaction.objects.get(id=id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(reaction.modifiers, many=True)
    return JSONResponse(serializer.data)

@api_view()
def get_reaction_modifier(request, reaction_id, modifier_id):
    try:
        reaction = Reaction.objects.get(id=reaction_id)
        modifier = reaction.modifiers.get(id=modifier_id)
    except Reaction.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(modifier)
    return JSONResponse(serializer.data)

@api_view()
def component_list(request):
    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))

    name = request.query_params.get('name', None)
    if name:
        components = ReactionComponent.objects.filter(
                Q(id__icontains=name) | 
                Q(long_name__icontains=name) | 
                Q(short_name__icontains=name)
            )[offset:(offset+limit)]
    else:
        components = ReactionComponent.objects.all()[offset:(offset+limit)]

    serializer = ReactionComponentSerializer(components, many=True)
    return JSONResponse(serializer.data)

@api_view()
def get_component(request, id):
    try:
        component = ReactionComponent.objects.get(id=id)
    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    serializer = ReactionComponentSerializer(component)
    return JSONResponse(serializer.data)

@api_view()
def currency_metabolite_list(request, id):
    try:
        component = ReactionComponent.objects.get(id=id)
    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    serializer = CurrencyMetaboliteSerializer(component.currency_metabolites, many=True)
    return JSONResponse(serializer.data)

@api_view()
def component_expression_list(request, id):
    tissue = request.query_params.get('tissue', '')
    expression_type = request.query_params.get('expression_type', '')
    expressions = ExpressionData.objects.filter(
            Q(reaction_component=id) &
            Q(tissue__icontains=tissue) & 
            Q(expression_type__icontains=expression_type)
        )

    serializer = ExpressionDataSerializer(expressions, many=True)
    return JSONResponse(serializer.data)

@api_view()
def interaction_partner_list(request, id):
    try:
        component = ReactionComponent.objects.get(id=id)
    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    reactions = list(chain(component.reactions_as_reactant.all(), component.reactions_as_product.all(), component.reactions_as_modifier.all()))
    serializer = InteractionPartnerSerializer(reactions, many=True)
    return JSONResponse(serializer.data)

@api_view()
def enzyme_list(request):
    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))

    enzymes = ReactionComponent.objects.filter(component_type='enzyme')[offset:(offset+limit)]

    serializer = ReactionComponentSerializer(enzymes, many=True)
    return JSONResponse(serializer.data)

@api_view()
def connected_metabolites(request, id):
    tissue = request.query_params.get('tissue', '')
    expression_type = request.query_params.get('expression_type', '')
    include_expressions = request.query_params.get('include_expression', '') == 'true' 
    
    enzyme = ReactionComponent.objects.get(
            Q(component_type='enzyme') &
            Q(long_name=id)
        )

    as_reactant = [MetaboliteReaction(r, 'reactant') for r in enzyme.reactions_as_reactant.all()]
    as_product = [MetaboliteReaction(r, 'product') for r in enzyme.reactions_as_product.all()]
    as_modifier = [MetaboliteReaction(r, 'modifier') for r in enzyme.reactions_as_modifier.all()]
    reactions = as_reactant + as_product + as_modifier

    expressions = ExpressionData.objects.filter(
            Q(gene_id=enzyme.id) &
            Q(tissue__icontains=tissue) & 
            Q(expression_type__icontains=expression_type)
        )

    connected_metabolites = ConnectedMetabolites(enzyme, enzyme.compartment, reactions, expressions)
    serializer = ConnectedMetabolitesSerializer(connected_metabolites)
    return JSONResponse(serializer.data)

