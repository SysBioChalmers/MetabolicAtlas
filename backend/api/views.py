from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from itertools import chain
from api.models import GEM, Author
from api.serializers import *

import re
import logging

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@api_view()
def model_list(request):
    models = GEM.objects.all()
    serializer = GEMSerializer(models, many=True)
    return JSONResponse(serializer.data)

@api_view()
def get_model(request, id):
    try:
        model = GEM.objects.get(id=id)
    except GEM.DoesNotExist:
        return HttpResponse(status=404)

    serializer = GEM(model)
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
        component = ReactionComponent.objects.get(Q(id=id) |
                                                  Q(long_name=id))
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
def get_component_with_interaction_partners(request, id):
    try:
        component = ReactionComponent.objects.get(Q(id=id) | Q(long_name=id))
    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    component_serializer = ReactionComponentSerializer(component)

    reactions_count = component.reactions_as_reactant.count() + \
            component.reactions_as_product.count() + \
            component.reactions_as_modifier.count()

    if reactions_count > 100:
        return HttpResponse(status=406)

    reactions = list(chain(
        component.reactions_as_reactant.all(),
        component.reactions_as_product.all(),
        component.reactions_as_modifier.all()
    ))
    reactions_serializer = InteractionPartnerSerializer(reactions, many=True)

    result = {
             'component': component_serializer.data,
             'reactions': reactions_serializer.data
             }

    return JSONResponse(result)

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

    try:
        enzyme = ReactionComponent.objects.get(
                Q(component_type='enzyme') &
                (Q(id=id) | Q(long_name=id))
            )
    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    reactions_count = enzyme.reactions_as_reactant.count() \
                        + enzyme.reactions_as_product.count() \
                        + enzyme.reactions_as_modifier.count()

    if reactions_count > 10:
        reactions = Reaction.objects.filter(
                Q(reactionreactant__reactant_id=enzyme.id) |
                Q(reactionproduct__product_id=enzyme.id) |
                Q(reactionmodifier__modifier_id=enzyme.id)
                ).distinct()
        serializer = ReactionSerializer(reactions, many=True)
        result = serializer.data

        return JSONResponse(result)

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

@api_view()
def expressions_list(request, enzyme_id):
    tissue = request.query_params.get('tissue', '')
    expression_type = request.query_params.get('expression_type', '')

    expressions = ExpressionData.objects.filter(
            Q(gene_id__icontains=enzyme_id) &
            Q(tissue__icontains=tissue) &
            Q(expression_type__icontains=expression_type)
        )

    serializer = ExpressionDataSerializer(expressions, many=True)
    return JSONResponse(serializer.data)

@api_view()
def get_metabolite_reactions(request, reaction_component_id):
    try:
        component = ReactionComponent.objects.get(Q(id=reaction_component_id) |
                                                  Q(long_name=reaction_component_id))

    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    if component.component_type != 'metabolite':
        return HttpResponseBadRequest('The provided reaction component is not a metabolite.')

    reactions = Reaction.objects.filter(Q(reactionproduct__product_id=reaction_component_id) |
                                        Q(reactionreactant__reactant_id=reaction_component_id))

    serializer = ReactionSerializer(reactions, many=True)
    result = serializer.data

    return JSONResponse(result)

@api_view()
def get_metabolite_reactome(request, reaction_component_id, reaction_id):
    try:
        component = ReactionComponent.objects.get(id=reaction_component_id)
        reaction = Reaction.objects.get(id=reaction_id)
    except ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    if component.component_type != 'metabolite':
        return HttpResponseBadRequest('The provided reaction component is not a metabolite.')

    modifiers = ReactionComponent.objects.filter(reactionmodifier__reaction_id=reaction.id)
    __reactants = ReactionComponent.objects.filter(reactionreactant__reaction_id=reaction.id)
    __products = ReactionComponent.objects.filter(reactionproduct__reaction_id=reaction.id)

    reactants = map(lambda
            rc: CurrencyMetaboliteReactionComponent(
                reaction_component=rc,
                reaction_id = reaction.id),
            __reactants)
    products = map(lambda
            rc: CurrencyMetaboliteReactionComponent(
                reaction_component=rc,
                reaction_id = reaction.id),
            __products)

    reaction_serializer = ReactionSerializer(reaction)
    modifiers_serializer = ReactionComponentSerializer(modifiers, many=True)
    reactants_serializer = CurrencyMetaboliteReactionComponentSerializer(reactants, many=True)
    products_serializer = CurrencyMetaboliteReactionComponentSerializer(products, many=True)

    result = reaction_serializer.data
    result['modifiers'] = modifiers_serializer.data
    result['reactants'] = reactants_serializer.data
    result['products'] = products_serializer.data

    return JSONResponse(result)


def rewriteEquation(term):
    # TODO there is probably something better to do here
    term = term.replace("+", " + ")
    term = term.replace("=>", " => ")
    term = re.sub("\\s{2,}", " ", term)
    term = term.strip()
    term = re.sub("(NA|NADP|H)\s\+\s\[", "\g<1>+[", term, flags=re.IGNORECASE)
    term = re.sub("(NA|NADP|H)\s\+(\s=>|$)", "\g<1>+\g<2>", term, flags=re.IGNORECASE)
    rp = term.split('=>')
    if len(rp) > 1:
        reactants = rp[0].split(' + ')
        for i in range(len(reactants)):
            reactants[i] = reactants[i].strip()
            if reactants[i] and not re.match(".+\[.\]$", reactants[i]):
                reactants[i] = reactants[i] + "[_]"
        products = rp[1].split(' + ')
        for i in range(len(products)):
            products[i] = products[i].strip()
            if products[i] and not re.match(".+\[.\]$", products[i]):
                products[i] = products[i] + "[_]"
        reactants = " + ".join(reactants)
        products = " + ".join(products)
        return "%%%s => %s%%" % (reactants, products)
    else:
        elements = rp[0].split(' + ')
        for i in range(len(elements)):
            elements[i] = elements[i].strip()
            if elements[i] and not re.match(".+\[.\]$", elements[i]):
                elements[i] = elements[i] + "[_]"

        elements = " + ".join(elements)
        return "%%%s%%" % elements


@api_view()
def search(request, term, truncated):

    if len(term.strip()) < 2:
        return HttpResponse(status=404)

    if truncated:
        limit = 50
    else:
        # limit the size anyway
        limit = 1000

    metabolites = Metabolite.objects.filter(
        Q(kegg__iexact=term) |
        Q(hmdb__iexact=term) |
        Q(hmdb_name__icontains=term)
    )

    enzymes = Enzyme.objects.filter(
        Q(uniprot_acc__iexact=term)
    )

    compartments = Compartment.objects.filter(name__icontains=term)

    subsystems = Subsystem.objects.filter(
        Q(name__icontains=term) |
        Q(external_id__iexact=term)
    )

    reactions = []
    term = term.replace("→", "=>")
    term = term.replace("⇨", "=>")
    if term.strip() not in ['+', '=>']:
        termEq = re.sub("[\(\[\{]\s?(.)\s?[\)\]\}]", "[\g<1>]", term)

        reactions = Reaction.objects.filter(
            Q(name__icontains=term) |
            Q(equation__icontains=termEq) |
            Q(ec__iexact=term) |
            Q(sbo_id__iexact=term)
        )[:limit]

        termEq = None
        reactions2 = []
        if '+' in term or '=>' in term:
            termEq = rewriteEquation(term)
            reactions2 = Reaction.objects.extra(
                where=["reaction::text ILIKE %s"], params=[termEq]
            )[:limit]

        reactions = list(chain(reactions, reactions2))

    components = ReactionComponent.objects.filter(
            Q(id__icontains=term) |
            Q(short_name__icontains=term) |
            Q(long_name__icontains=term) |
            Q(formula__icontains=term) |
            Q(metabolite__in=metabolites) |
            Q(enzyme__in=enzymes)
        ).order_by('short_name')[:limit]

    if (components.count() + compartments.count() + subsystems.count() + len(reactions))== 0:
        return HttpResponse(status=404)

    RCserializer = ReactionComponentSearchSerializer(components, many=True)
    compartmentSerializer = CompartmentSerializer(compartments, many=True)
    subsystemSerializer = SubsystemSerializer(subsystems, many=True)
    reactionSerializer = ReactionSearchSerializer(reactions, many=True)

    results = {
        'reactionComponent': RCserializer.data,
        'compartment': compartmentSerializer.data,
        'subsystem': subsystemSerializer.data,
        'reaction': reactionSerializer.data
    }

    return JSONResponse(results)

@api_view(['POST'])
def convert_to_reaction_component_ids(request, compartmentID):
    arrayTerms = [el.strip() for el in request.data['data'] if len(el) != 0]
    query = Q()
    for term in arrayTerms:
        query |= Q(id__iexact=term)
        query |= Q(short_name__iexact=term)
        query |= Q(long_name__iexact=term)

    if str(compartmentID) != '0':
        reactionComponents = ReactionComponent.objects.filter(query & Q(compartment=compartmentID)).values_list('compartment_id', 'id')
    else:
        reactionComponents = ReactionComponent.objects.filter(query).values_list('compartment_id', 'id').distinct()

    if reactionComponents.count() == 0:
        return HttpResponse(status=404)

    return JSONResponse(reactionComponents);


@api_view()
def get_gemodel(request, id):
    try:
        model = GEModel.objects.get(id=id)
    except GEModel.DoesNotExist:
        return HttpResponse(status=404)

    logging.warn(model)
    serializer = GEModelSerializer(model)
    logging.warn(serializer.data)
    return JSONResponse(serializer.data)


@api_view()
def get_gemodels(request):
    import urllib
    import json
    import base64
    # get models from database
    serializer = GEModelListSerializer(GEModel.objects.all(), many=True)
    # serializer = None
    # get models from git
    list_repo = []
    try:
        URL = 'https://api.github.com/orgs/SysBioChalmers/repos'
        result = urllib.request.urlopen(URL)
        list_repo = json.loads(result.read().decode('UTF-8'))
    except Exception as e:
        logging.warn(e)
        pass
        # return HttpResponse(status=400)

    for repo in list_repo:
        logging.warn(repo['name'])
        if repo['name'].startswith('GEM_') or False:
            try:
                result = urllib.request.urlopen(repo['url'] + '/contents/README.md?ref=master')
                readme = json.loads(result.read().decode('UTF-8'))['content']
            except Exception as e:
                logging.warn(e)
                continue

            readme_content = base64.b64decode(readme)
            logging.warn(readme)
            d = parse_readme_file(readme_content)
            # TODO make GEM objects and json to current serializer

            break

    return JSONResponse(serializer.data)


def parse_readme_file(content):
    d = {}
    key_entry = {
        'name': 'label',
    }
    parse_entries = False
    for line in content.decode('UTF-8'):
        if line.startswith("| Name |"):
            if not parse_entries:
                parse_entries = True
            else:
                break

        if parse_entries:
            entry, value = line.split('\t')
            d[key_entry[entry]] = value.strip()

    return d
