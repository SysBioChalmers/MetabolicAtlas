from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from itertools import chain
from rest_framework import permissions
import api.models as APImodels
import api.serializers as APIserializer
import api.serializers_rc as APIrcSerializer

import requests
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
    serializer_choice = ['basic', 'lite', 'table', 'search', None]
    if serializer_type not in serializer_choice:
        raise ValueError("Error serializer type, choices are %s" % ", ".join([str(e) for e in serializer_choice]))

    if database in ['hmr2', 'hmr2n', 'hmr3']:
        if type == 'reaction component':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.ReactionComponentLiteSerializer
            return APIrcSerializer.HmrReactionComponentSerializer
        elif type == 'metabolite':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.HmrMetaboliteReactionComponentLiteSerializer
            if serializer_type in ['search']:
                return APIrcSerializer.MetaboliteReactionComponentSearchSerializer
            return APIrcSerializer.HmrMetaboliteReactionComponentSerializer
        elif type == 'enzyme':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.HmrEnzymeReactionComponentLiteSerializer
            elif serializer_type in ['search']:
                return APIrcSerializer.EnzymeReactionComponentSearchSerializer
            return APIrcSerializer.HmrEnzymeReactionComponentSerializer
        elif type == 'reaction':
            if serializer_type == 'basic':
                return APIserializer.HmrReactionBasicSerializer
            if serializer_type == 'lite':
                return APIserializer.HmrReactionLiteSerializer
            if serializer_type == 'table':
                return APIserializer.HmrReactionBasicRTSerializer
            if serializer_type == 'search':
                return APIserializer.ReactionSearchSerializer
            return APIserializer.HmrReactionSerializer
        elif type == 'subsystem':
            if serializer_type == 'lite':
                return APIserializer.SubsystemLiteSerializer
            elif serializer_type == 'search':
                return APIserializer.SubsystemSearchSerializer
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
            elif serializer_type in ['search']:
                return APIrcSerializer.MetaboliteReactionComponentSearchSerializer
            return APIrcSerializer.MetaboliteReactionComponentSerializer
        elif type == 'enzyme':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.ReactionComponentSerializer
            if serializer_type in ['search']:
                return APIrcSerializer.EnzymeReactionComponentSearchSerializer
            return APIrcSerializer.EnzymeReactionComponentSerializer
        elif type == 'reaction':
            if serializer_type == 'basic':
                return APIserializer.ReactionBasicSerializer
            if serializer_type == 'lite':
                return APIserializer.ReactionLiteSerializer
            if serializer_type == 'table':
                return APIserializer.HmrReactionBasicRTSerializer
            if serializer_type == 'search':
                return APIserializer.ReactionSearchSerializer
            return APIserializer.ReactionSerializer
        elif type == 'subsystem':
            if serializer_type == 'lite':
                return APIserializer.SubsystemLiteSerializer
            elif serializer_type =='search':
                return APIserializer.SubsystemSearchSerializer
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

    pmids = APImodels.ReactionReference.objects.using(model).filter(reaction_id=reaction.id)
    pmidserializer = APIserializer.ReactionReferenceSerializer(pmids, many=True)

    return JSONResponse({'reaction': reactionserializer.data,
                         'pmids': pmidserializer.data})


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


@api_view()
def get_metabolite_interaction_partners(request, model, id):
    """
        For a given metabolite, pull out all first order interaction partners.
    """
    response = get_interaction_partners(request=request._request, model=model, id=id, type='m')
    return response


@api_view()
def get_enzyme_interaction_partners(request, model, id):
    """
        For a given enzyme, pull out all first order interaction partners.
    """
    response = get_interaction_partners(request=request._request, model=model, id=id, type='e')
    return response


@api_view()
@is_model_valid
def get_interaction_partners(request, model, id, type=None):
    try:
        component = APImodels.ReactionComponent.objects.using(model).get(id__iexact=id)
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    reactions = []
    if type == 'm':
        reactions = component.reactions_as_metabolite.prefetch_related('reactants', 'products', 'modifiers').all()
    elif type == 'e':
        reactions = component.reactions_as_modifier.prefetch_related('reactants', 'products', 'modifiers').all()

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
    Return all information for a given enzyme (for example ENSG00000196502 or SULTA1).
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
    List metabolites in the given model
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
        Return all information for a given metabolite (for example m01587m or citrate[m]).
    """
    try:
        component = APImodels.ReactionComponent.objects.using(model).get(Q(id__iexact=id) |
                                                                         Q(full_name__iexact=id))
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
        supply a metabolite ID or its name (for example m02439c or malate).
    """
    component = APImodels.ReactionComponent.objects.using(model).filter((Q(id__iexact=id) |
                                                                         Q(full_name__iexact=id)) &
                                                                         Q(component_type='m'))
    if not component:
        return HttpResponse(status=404)

    if all_compartment:
        component = APImodels.ReactionComponent.objects.using(model).filter(Q(name=component[0].name) &
                                                                                Q(component_type='m'))

    reactions = APImodels.Reaction.objects.none()
    for c in component:
        reactions_as_met = c.reactions_as_metabolite.using(model). \
            prefetch_related('reactants', 'products', 'modifiers').distinct()
        # reactions_as_products = c.reactions_as_product.using(model). \
        # prefetch_related('reactants', 'products', 'modifiers').distinct()
        reactions |= reactions_as_met

    reactions = reactions.distinct()
    ReactionSerializerClass= componentDBserializerSelector(model, 'reaction', serializer_type='table', api_version=request.version)
    serializer = ReactionSerializerClass(reactions[:200], many=True, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_enzyme_reactions(request, model, id):
    """
        list in which reactions does a given enzyme occur,
        supply a enzyme/gene ID or its name (for example ENSG00000180011).
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


@api_view()
@is_model_valid
def get_subsystem(request, model, subsystem_name_id, api=True):
    """
        For a given subsystem name, get all containing metabolites, enzymes.
    """
    try:
        subsystem = APImodels.Subsystem.objects.using(model).get(Q(name_id__iexact=subsystem_name_id) | Q(name__iexact=subsystem_name_id))
        subsystem_id = subsystem.id
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    SubsystemSerializerClass = componentDBserializerSelector(model, 'subsystem', serializer_type='lite', api_version=request.version)
    if not api:
        limit = 1000
        smsQuerySet = APImodels.ReactionComponent.objects.using(model).filter(subsystem_metabolite__id=subsystem_id)[:limit]
        sesQuerySet = APImodels.ReactionComponent.objects.using(model).filter(subsystem_enzyme__id=subsystem_id)[:limit]
        results = {
            'info': SubsystemSerializerClass(subsystem, context={'model': model}).data,
            'metabolites': APIrcSerializer.ReactionComponentLiteSerializer(smsQuerySet, many=True, context={'model': model}).data,
            'enzymes': APIrcSerializer.ReactionComponentLiteSerializer(sesQuerySet, many=True, context={'model': model}).data,
            'limit': limit
         }
    else:
        smsQuerySet = APImodels.SubsystemMetabolite.objects.using(model). \
            filter(subsystem_id=subsystem_id).values_list('rc_id', flat=True)
        sesQuerySet = APImodels.SubsystemEnzyme.objects.using(model). \
            filter(subsystem_id=subsystem_id).values_list('rc_id', flat=True)

        results = {}
        results.update(SubsystemSerializerClass(s, context={'model': model}).data)
        results['metabolites'] =  smsQuerySet
        results['enzymes'] =  sesQuerySet

    return JSONResponse(results)


@api_view()
@is_model_valid
def get_subsystem_reactions(request, model, subsystem_name_id, api=True):
    """
        For a given subsystem name, get all containing reactions.
    """
    try:
        subsystem = APImodels.Subsystem.objects.using(model).get(Q(name_id__iexact=subsystem_name_id) | Q(name__iexact=subsystem_name_id))
        subsystem_id = subsystem.id
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    if api:
        r = APImodels.Reaction.objects.using(model).filter(subsystem=subsystem_id). \
            prefetch_related('modifiers').distinct()
    else:
        r = APImodels.Reaction.objects.using(model).filter(subsystem=subsystem_id). \
            prefetch_related('modifiers').distinct()[:1000]

    ReactionSerializerClass= componentDBserializerSelector(model, 'reaction', serializer_type='table', api_version=request.version)
    results = {
        'reactions': ReactionSerializerClass(r, many=True, context={'model': model}).data,
        'limit': 1000,
    }

    if api:
        return JSONResponse(results['reactions'])
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
        List all compartments for the given model.
    '''
    try:
        compartment = APImodels.Compartment.objects.using(model).all()
    except APImodels.Compartment.DoesNotExist:
        return HttpResponse(status=404)

    serializer = APIserializer.CompartmentSerializer(compartment, many=True)

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_compartment(request, model, compartment_name_id, api=True):
    # api is false when this function is called from the compartment page
    # false when called using the swagger api
    """
        For a given compartment name, get all containing metabolites, enzymes, reactions and subsystems.
    """
    try:
        compartment = APImodels.Compartment.objects.using(model).get(Q(name_id__iexact=compartment_name_id) | Q(name__iexact=compartment_name_id))
        compartment_id = compartment.id
    except APImodels.Compartment.DoesNotExist:
        return HttpResponse(status=404)

    subsystems = APImodels.SubsystemCompartment.objects.using(model).filter(compartment_id=compartment_id). \
        prefetch_related('subsystem').distinct().values_list('subsystem__name', flat=True)

    if not api:
        results = {
            'info': APIserializer.CompartmentSerializer(compartment, context={'model': model}).data,
            'subsystems': subsystems,
        }
    else:
        sms = APImodels.ReactionComponentCompartment.objects.using(model).filter(compartment_id=compartment_id).values_list('rc_id', flat=True)
        ses = APImodels.CompartmentEnzyme.objects.using(model).filter(compartment_id=compartment_id).values_list('rc_id', flat=True)
        reactions = APImodels.ReactionCompartment.objects.using(model).filter(compartment_id=compartment_id).values_list('reaction_id', flat=True)

        results = {}
        results.update(APIserializer.CompartmentSerializer(compartment, context={'model': model}).data)
        results['metabolite'] = sms
        results['enzymes'] = ses
        results['reactions'] = reactions

    return JSONResponse(results)


#=========================================================================================================
# For the integrated Models stored in separate database

@api_view()
def get_models(request):
    """
    List all Genome-scale metabolic models (GEMs) that are available on the GEM browser,
    """
    models = APImodels.GEM.objects.all()
    serializer = APIserializer.GEMSerializer(models, many=True)
    return JSONResponse(serializer.data)



@api_view()
def get_model(request, model_id):
    """
    Return all known information for a given model available on the GEM browser, supply its ID (int) or database_name e.g. 'human1'
    """

    try:
        int(model_id)
        is_int = True
    except ValueError:
        is_int = False

    try:
        if is_int:
            model = APImodels.GEM.objects.filter(id=model_id).select_related('sample').prefetch_related('authors', 'ref')
        else:
            model = APImodels.GEM.objects.filter(database_name__iexact=model_id).select_related('sample').prefetch_related('authors', 'ref')
    except APImodels.GEM.DoesNotExist:
        return HttpResponse(status=404)

    serializer = APIserializer.GEMSerializer(model[0])
    return JSONResponse(serializer.data)
