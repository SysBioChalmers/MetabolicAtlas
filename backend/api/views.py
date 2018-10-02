from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from itertools import chain
from rest_framework import permissions
from django.conf import settings
import api.models as APImodels
import api.serializers as APIserializer
import api.serializers_rc as APIrcSerializer

import requests
import re
import logging
import functools

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def is_model_valid(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        model = kwargs.get('model')
        if not model:
            model = args.get('model')
        try:
            m = APImodels.GEM.objects.get(database_name=model)
        except APImodels.GEM.DoesNotExist:
            return HttpResponse("Invalid model name '%s'" % model, status=404)
        return view_func(request, *args, **kwargs)
    return wrapper


class IsModelValid(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            APImodels.GEM.objects.get(database_name=request.model)
        except APImodels.GEM.DoesNotExist:
            return False
        return True


def componentDBserializerSelector(database, type, serializer_type=None, api_version=None):
    serializer_choice = ['basic', 'lite', 'table', None]
    if serializer_type not in serializer_choice:
        raise ValueError("Error serializer type, choices are %s" % ", ".join(serializer_choice))

    if database in ['hmr2', 'hmr2n', 'hmr3']:
        if type == 'reaction component':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.ReactionComponentLiteSerializer
            return APIrcSerializer.HmrReactionComponentSerializer
        elif type == 'metabolite':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.HmrMetaboliteReactionComponentLiteSerializer
            return APIrcSerializer.HmrMetaboliteReactionComponentSerializer
        elif type == 'enzyme':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.HmrEnzymeReactionComponentLiteSerializer
            return APIrcSerializer.HmrEnzymeReactionComponentSerializer
        elif type == 'reaction':
            if serializer_type == 'basic':
                return APIserializer.HmrReactionBasicSerializer
            if serializer_type == 'lite':
                return APIserializer.HmrReactionLiteSerializer
            if serializer_type == 'table':
                return APIserializer.HmrReactionBasicRTSerializer
            return APIserializer.HmrReactionSerializer
        elif type == 'subsystem':
            return APIserializer.HmrSubsystemSerializer
        elif type == 'interaction partner':
            if serializer_type == 'lite':
                return APIserializer.HmrInteractionPartnerLiteSerializer
            return APIserializer.HmrInteractionPartnerSerializer
    else:
        if type == 'reaction component':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.ReactionComponentLiteSerializer
            return APIrcSerializer.ReactionComponentSerializer
        elif type == 'metabolite':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.ReactionComponentSerializer
            return APIrcSerializer.ReactionComponentSerializer
        elif type == 'enzyme':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.ReactionComponentSerializer
            return APIrcSerializer.ReactionComponentSerializer
        elif type == 'reaction':
            if serializer_type == 'basic':
                return APIserializer.ReactionBasicSerializer    
            if serializer_type == 'lite':
                return APIserializer.ReactionLiteSerializer
            if serializer_type == 'table':
                return APIserializer.HmrReactionBasicRTSerializer
            return APIserializer.ReactionSerializer
        elif type == 'subsystem':
            return APIserializer.SubsystemSerializer
        elif type == 'interaction partner':
            if serializer_type == 'lite':
                return APIserializer.InteractionPartnerLiteSerializer
            return APIserializer.InteractionPartnerSerializer



@api_view()
@is_model_valid
def get_reactions(request, model):
    """
    Returns all reactions for the given model
    """
    limit = int(request.query_params.get('limit', 10000))
    offset = int(request.query_params.get('offset', 0))
    reactions = APImodels.Reaction.objects.using(model).all()[offset:(offset+limit)]

    serializerClass = componentDBserializerSelector(model, 'reaction', serializer_type="basic", api_version=request.version)

    serializer = serializerClass(reactions, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_reaction(request, model, id):
    """
    Returns all the information we have about a reaction (for example HMR_3905).
    """
    try:
        reaction = APImodels.Reaction.objects.using(model).get(id__iexact=id)
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    ReactionSerializerClass = componentDBserializerSelector(model, 'reaction', serializer_type='lite', api_version=request.version)
    reactionserializer = ReactionSerializerClass(reaction, context={'model': model})

    # TODO move that in the javascript
    pmids = APImodels.ReactionReference.objects.using(model).filter(reaction_id=id)
    if pmids.count():
        pmidserializer = APIserializer.ReactionReferenceSerializer(pmids, many=True)
        url = ('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
               '?db=pubmed&retmode=json&id={}'.format(
                   ','.join([x['pmid'].replace('PMID:', '')
                             for x in pmidserializer.data])))
        pmidsresponse = requests.get(url).json()['result']
    else:
        pmidsresponse = {}

    return JSONResponse({'reaction': reactionserializer.data,
                         'pmids': pmidsresponse})


@api_view()
@is_model_valid
def get_reaction_reactants(request, model, id):
    """
    For a given reaction returns all the metabolites that are consumed.
    """
    try:
        reaction = APImodels.Reaction.objects.using(model).prefetch_related('reactants__metabolite').get(id__iexact=id)
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    ReactantsSerializerClass = componentDBserializerSelector(model, 'metabolite', serializer_type='lite', api_version=request.version)
    serializer = ReactantsSerializerClass(reaction.reactants, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_reaction_products(request, model, id):
    """
    For a given reaction show the metabolites that are produced.
    """
    try:
        reaction = APImodels.Reaction.objects.using(model).prefetch_related('products__metabolite').get(id__iexact=id)
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    ProductsSerializerClass = componentDBserializerSelector(model, 'metabolite', serializer_type='lite', api_version=request.version)
    serializer = ProductsSerializerClass(reaction.products, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_reaction_modifiers(request, model, id):
    """
    For a given reaction returns the proteins that are modifying it.
    """
    try:
        reaction = APImodels.Reaction.objects.using(model).prefetch_related('modifiers__enzyme').get(id__iexact=id)
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    EnzymesSerializerClass = componentDBserializerSelector(model, 'enzyme', serializer_type='lite', api_version=request.version)
    serializer = EnzymesSerializerClass(reaction.modifiers, many=True, context={'model': model})
    return JSONResponse(serializer.data)


'''@api_view()
def currency_metabolite_list(request, model, id):
    """
    For a given reaction component, list all reactions in which its a currency metabolite,
    supply an id (for example M_m00003c)
    """
    try:
        component = APImodels.ReactionComponent.objects.using(model).get(id__iexact=id)
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    serializer = APIserializer.CurrencyMetaboliteSerializer(component.currency_metabolites, many=True)
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
   return JSONResponse(serializer.data)'''


@api_view()
def get_metabolite_interaction_partners(request, model, id):
    """
        For a given metabolite, pull out all first order interaction partners.
    """
    response = get_interaction_partners(request=request._request, model=model, id=id)
    return response


@api_view()
def get_enzyme_interaction_partners(request, model, id):
    """
        For a given enzyme, pull out all first order interaction partners.
    """
    response = get_interaction_partners(request=request._request, model=model, id=id)
    return response


@api_view()
@is_model_valid
def get_interaction_partners(request, model, id):
    try:
        component = APImodels.ReactionComponent.objects.using(model).get(Q(id__iexact=id) | Q(name__iexact=id))
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    reactions = list(chain(
        component.reactions_as_reactant.prefetch_related('reactants', 'products', 'modifiers').all(),
        component.reactions_as_product.prefetch_related('reactants', 'products', 'modifiers').all(),
        component.reactions_as_modifier.prefetch_related('reactants', 'products', 'modifiers').all()
        )
    )
    InteractionPartnerSerializerClass = componentDBserializerSelector(model, 'interaction partner', serializer_type="lite", api_version=request.version)
    serializer = InteractionPartnerSerializerClass(reactions, many=True)
    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_enzymes(request, model):
    """
    List enzymes in the given model
    """
    limit = int(request.query_params.get('limit', 10000))
    offset = int(request.query_params.get('offset', 0))

    enzymes = APImodels.ReactionComponent.objects.using(model).filter(component_type='e').select_related('enzyme')[offset:(offset+limit)]

    EnzymeSerializerClass = componentDBserializerSelector(model, 'enzyme', api_version=request.version)
    serializer = EnzymeSerializerClass(enzymes, many=True, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_enzyme(request, model, id):
    """
    Return all information for a given enzyme (for example ENSG00000108839).
    """
    try:
        component = APImodels.ReactionComponent.objects.using(model).get(Q(id__iexact=id) |
                                                                         Q(name__iexact=id))
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    if component.component_type == 'm':
        return HttpResponse(status=404)

    serializerClass = componentDBserializerSelector(model, 'enzyme', api_version=request.version)
    serializer = serializerClass(component, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_metabolites(request, model):
    """
    List enzymes in the given model
    """
    limit = int(request.query_params.get('limit', 10000))
    offset = int(request.query_params.get('offset', 0))

    enzymes = APImodels.ReactionComponent.objects.using(model).filter(component_type='m').select_related('metabolite')[offset:(offset+limit)]

    MetaboliteSerializerClass = componentDBserializerSelector(model, 'metabolite', api_version=request.version)
    serializer = MetaboliteSerializerClass(enzymes, many=True, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_metabolite(request, model, id):
    """
    Return all information for a given enzyme (for example ENSEMBL0001256).
    """
    try:
        component = APImodels.ReactionComponent.objects.using(model).get(Q(id__iexact=id) |
                                                                         Q(name__iexact=id))
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    if component.component_type == 'e':
        return HttpResponse(status=404)

    serializerClass = componentDBserializerSelector(model, 'metabolite', api_version=request.version)
    serializer = serializerClass(component, context={'model': model})

    return JSONResponse(serializer.data)



@api_view()
@is_model_valid
def get_metabolite_reactions(request, model, id, all_compartment=False):
    """
        list in which reactions does a given metabolite occur,
        supply a metabolite id (for example m00003c).
    """
    component = APImodels.ReactionComponent.objects.using(model).filter((Q(id__iexact=id) |
                                                                         Q(name__iexact=id)) &
                                                                         Q(component_type='m'))
    if not component:
        return HttpResponse(status=404)

    if all_compartment:
        component = APImodels.ReactionComponent.objects.using(model).filter(Q(name=component[0].name) &
                                                                                Q(component_type='m'))

    reactions = APImodels.Reaction.objects.none()
    for c in component:
        reactions_as_reactant = c.reactions_as_reactant.using(model). \
        prefetch_related('reactants', 'products', 'modifiers').distinct()
        reactions_as_products = c.reactions_as_product.using(model). \
        prefetch_related('reactants', 'products', 'modifiers').distinct()
        reactions |= (reactions_as_reactant | reactions_as_products)
        reactions = reactions.distinct()

    ReactionSerializerClass= componentDBserializerSelector(model, 'reaction', serializer_type='table', api_version=request.version)
    serializer = ReactionSerializerClass(reactions[:200], many=True, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_enzyme_reactions(request, model, id):
    """
        list in which reactions does a given enzyme occur,
        supply a metabolite id (for example ENSG00000180011).
    """
    component = APImodels.ReactionComponent.objects.using(model).filter((Q(id__iexact=id) |
                                                                         Q(name__iexact=id)) &
                                                                         Q(component_type='e'))

    if not component:
        return HttpResponse(status=404)

    reactions = APImodels.Reaction.objects.none()
    for c in component:
        reactions_as_modifier = c.reactions_as_modifier.using(model). \
        prefetch_related('reactants', 'products', 'modifiers').distinct()
        reactions |= reactions_as_modifier
        reactions = reactions.distinct()

    ReactionSerializerClass= componentDBserializerSelector(model, 'reaction', serializer_type='table', api_version=request.version)
    serializer = ReactionSerializerClass(reactions[:200], many=True, context={'model': model})

    return JSONResponse(serializer.data)


def rewriteEquation(term):
    # TODO there is probably something better to do here
    # fix compartment letter size
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
def search(request, model, term):
    """
        Searches for the term in metabolites, enzymes, reactions, subsystems and compartments.
    """

    # l = logging.getLogger('django.db.backends')
    # l.setLevel(logging.DEBUG)
    # l.addHandler(logging.StreamHandler())

    term = term.replace(";", "#")
    term = term.strip()

    if len(term) < 2:
        return HttpResponse("Invalid query, term must be at least 2 characters long", status=400)

    results = {}
    if model == 'all':
        models = [k for k in settings.DATABASES if k not in ['default', 'gems']]
        limit = 10000
    else:
        try:
            APImodels.GEM.objects.get(database_name=model)
        except APImodels.GEM.DoesNotExist:
            return HttpResponse("Invalid model name '%s'" % model, status=404)
        models = [model]
        limit = 50

    match_found = False
    for model in models:
        if model not in results:
            results[model] = {}

        compartments = APImodels.Compartment.objects.using(model).filter(name__icontains=term)

        subsystems = APImodels.Subsystem.objects.using(model).prefetch_related('compartment').filter(
            Q(name__icontains=term) |
            Q(external_id__iexact=term)
        )

        reactions = []
        term = term.replace("→", "=>")
        term = term.replace("⇒", "=>")
        term = term.replace("⇔", "=>")
        term = term.replace("->", "=>")
        if not term.strip() == '=>':
            termEqlike = False
            if '+' in term or '=>' in term:
                termEqlike = rewriteEquation(term)

            termEq = re.sub("[\(\[\{]\s?(.{1,3})\s?[\)\]\}]", "[\g<1>]", term)
            reactions = APImodels.Reaction.objects.using(model).filter(
                Q(id__iexact=term) |
                Q(name__icontains=term) |
                Q(equation__icontains=termEq) |
                Q(equation_wname__icontains=termEq) |
                Q(ec__icontains=term) |
                Q(sbo_id__iexact=term) |
                (Q(equation__ilike=termEqlike) if termEqlike else Q(pk__isnull=True))
            )[:limit]

        metabolites = APImodels.ReactionComponent.objects.using(model).select_related('metabolite').filter(
                Q(component_type__exact='m') &
                (Q(id__iexact=term) |
                Q(name__icontains=term) |
                Q(alt_name1__icontains=term) |
                Q(alt_name2__icontains=term) |
                Q(aliases__icontains=term) |
                Q(external_id1__iexact=term) |
                Q(external_id2__iexact=term) |
                Q(external_id3__iexact=term) |
                Q(external_id4__iexact=term) |
                Q(formula__icontains=term))
            )[:limit]

        enzymes = APImodels.ReactionComponent.objects.using(model).select_related('enzyme').filter(
                Q(component_type__exact='e') &
                (Q(id__iexact=term) |
                Q(name__icontains=term) |
                Q(alt_name1__icontains=term) |
                Q(alt_name2__icontains=term) |
                Q(aliases__icontains=term) |
                Q(external_id1__iexact=term) |
                Q(external_id2__iexact=term) |
                Q(external_id3__iexact=term) |
                Q(external_id4__iexact=term) |
                Q(formula__icontains=term))
            )[:limit]

        if (metabolites.count() + enzymes.count() + compartments.count() + subsystems.count() + reactions.count()) != 0:
            match_found = True

        MetaboliteSerializerClass = componentDBserializerSelector(model, 'metabolite', serializer_type='lite', api_version=request.version)
        EnzymeSerializerClass = componentDBserializerSelector(model, 'enzyme', serializer_type='lite', api_version=request.version)
        ReactionSerializerClass= componentDBserializerSelector(model, 'reaction', serializer_type='basic', api_version=request.version)
        SubsystemSerializerClass = componentDBserializerSelector(model, 'subsystem', serializer_type='lite', api_version=request.version)

        metaboliteSerializer = MetaboliteSerializerClass(metabolites, many=True)
        enzymeSerializer = EnzymeSerializerClass(enzymes, many=True)
        compartmentSerializer = APIserializer.CompartmentSerializer(compartments, many=True)
        subsystemSerializer = SubsystemSerializerClass(subsystems, many=True, context={'model': model})
        reactionSerializer = ReactionSerializerClass(reactions, many=True, context={'model': model})

        results[model]['metabolite'] = metaboliteSerializer.data
        results[model]['enzyme'] = enzymeSerializer.data
        results[model]['compartment'] = compartmentSerializer.data
        results[model]['subsystem'] = subsystemSerializer.data
        results[model]['reaction'] = reactionSerializer.data

        response = JSONResponse(results)

    if not match_found:
        return HttpResponse(status=404)

    return response


@api_view()
@is_model_valid
def get_subsystem(request, model, subsystem_name_id):
    """
    For a given subsystem name, get all containing metabolites, enzymes, and reactions.
    """
    try:
        subsystem = APImodels.Subsystem.objects.using(model).get(name_id__iexact=subsystem_name_id)
        subsystem_id = subsystem.id
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    try:
        s = APImodels.Subsystem.objects.using(model).get(id=subsystem_id)
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)



    smsQuerySet = APImodels.SubsystemMetabolite.objects.using(model).filter(subsystem_id=subsystem_id).select_related("rc")
    sesQuerySet = APImodels.SubsystemEnzyme.objects.using(model).filter(subsystem_id=subsystem_id).select_related("rc")

    r = APImodels.Reaction.objects.using(model).filter(subsystem=subsystem_id). \
    prefetch_related('modifiers').distinct()

    sms = []; ses = [];
    for m in smsQuerySet:
        sms.append(m.rc)
    for e in sesQuerySet:
        ses.append(e.rc)


    ReactionSerializerClass= componentDBserializerSelector(model, 'reaction', serializer_type='table', api_version=request.version)
    SubsystemSerializerClass = componentDBserializerSelector(model, 'subsystem', serializer_type='lite', api_version=request.version)

    results = {
        'subsystemAnnotations': SubsystemSerializerClass(s, context={'model': model}).data,
        'metabolites': APIrcSerializer.ReactionComponentLiteSerializer(sms, many=True, context={'model': model}).data,
        'enzymes': APIrcSerializer.ReactionComponentLiteSerializer(ses, many=True, context={'model': model}).data,
        'reactions': ReactionSerializerClass(r, many=True, context={'model': model}).data
    }

    return JSONResponse(results)


@api_view()
@is_model_valid
def get_subsystems(request, model):
    """
    List all subsystems/pathways/collection of reactions for the given model.
    """
    try:
        subsystems = APImodels.Subsystem.objects.using(model).all().prefetch_related('compartment')
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    serializerClass = componentDBserializerSelector(model, 'subsystem', api_version=request.version)
    serializer = serializerClass(subsystems, many=True, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_compartments(request, model):
    '''
        list all compartments for the given model.
    '''
    try:
        compartment = APImodels.Compartment.objects.using(model).all()
    except APImodels.Compartment.DoesNotExist:
        return HttpResponse(status=404)

    serializer = APIserializer.CompartmentSerializer(compartment, many=True)

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_compartment(request, model, compartment_name_id):
    '''
        return all information for the given compartment's name.
    '''
    try:
        compartment = APImodels.Compartment.objects.using(model).get(name_id__iexact=compartment_name_id)
    except APImodels.Compartment.DoesNotExist:
        return HttpResponse(status=404)

    serializer = APIserializer.CompartmentSerializer(compartment)

    return JSONResponse(serializer.data)



#=========================================================================================================
# For the Models database

@api_view()
def get_models(request):
    """
    List all Genome-scale metabolic models (GEMs) that are available on the GemsExplorer,
    """
    models = APImodels.GEM.objects.all()
    serializer = APIserializer.GEMListSerializer(models, many=True)
    return JSONResponse(serializer.data)


@api_view()
def get_model(request, model_id):
    """
    Return all known information for a given model available on the GemsExplorer, supply its ID (int) or database_name e.g. 'hmr3'
    """

    try: 
        int(model_id)
        is_int = True
    except ValueError:
        is_int = False

    try:
        if is_int:
            model = APImodels.GEM.objects.get(id=model_id)
        else:
            model = APImodels.GEM.objects.get(database_name__iexact=model_id)
    except APImodels.GEM.DoesNotExist:
        return HttpResponse(status=404)

    serializer = APIserializer.GEMSerializer(model)
    return JSONResponse(serializer.data)


@api_view()
def get_gemodels(request):
    """
    List all GEMs that the group have made
    """
    # get models from database

    serializer = APIserializer.GEModelListSerializer(APImodels.GEModel.objects.all(). \
        prefetch_related('gemodelset__reference', 'ref').select_related('gemodelset', 'sample'), many=True)

    return JSONResponse(serializer.data)


@api_view()
def get_gemodel(request, gem_id):
    """
    For a given Genome-scale metabolic model ID or label, pull out everything we know about it.
    """

    try: 
        int(gem_id)
        is_int = True
    except ValueError:
        is_int = False

    if is_int:
         model = APImodels.GEModel.objects.filter(id=gem_id). \
         prefetch_related('files', 'ref')
    else:
         if gem_id == "HMR2":
             gem_id = "HMR 2.0" # TODO fix . in url
         model = APImodels.GEModel.objects.filter(label__iexact=gem_id). \
             prefetch_related('files', 'ref')

    if not model:
        return HttpResponse(status=404)

    serializer = APIserializer.GEModelSerializer(model[0])
    return JSONResponse(serializer.data)
