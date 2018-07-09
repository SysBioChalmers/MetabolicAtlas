from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from itertools import chain
import api.models as APImodels
import api.serializers as APIserializer
import api.serializers_rc as APIrcSerializer
from api.views import is_model_valid
from api.views import componentDBserializerSelector

import requests
import re
import logging

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)



@api_view(['POST'])
@is_model_valid
def convert_to_reaction_component_ids(request, model, compartment_name=None):
    arrayTerms = [el.strip() for el in request.data['data'] if len(el) != 0]
    if not arrayTerms:
        return JSONResponse({})

    query = Q()
    reaction_query = Q()
    for term in arrayTerms:
        query |= Q(id__iexact=term)
        reaction_query |= Q(id__iexact=term)
        query |= Q(name__iexact=term)
        query |= Q(alt_name1__iexact=term)
        query |= Q(alt_name2__iexact=term)
        query |= Q(external_id1__iexact=term)
        query |= Q(external_id2__iexact=term)
        query |= Q(external_id3__iexact=term)
        query |= Q(external_id4__iexact=term)

    # get the list of component id
    reaction_component_ids = APImodels.ReactionComponent.objects.using(model).filter(query).values_list('id');

    # get the list of reaction id
    reaction_ids = APImodels.Reaction.objects.using(model).filter(reaction_query).values_list('id')

    if not reaction_component_ids and not reaction_ids:
        return HttpResponse(status=404)

    if not compartment_name:
        # get the compartment id for each component id
        rcci = APImodels.ReactionComponentCompartmentSvg.objects.using(model) \
        .filter(Q(rc_id__in=reaction_component_ids)) \
        .select_related('Compartmentsvg') \
        .values_list('compartmentsvg__display_name', 'rc_id')

        # get the compartment id for each reaction id
        rci = APImodels.ReactionCompartmentSvg.objects.using(model).filter(Q(reaction_id__in=reaction_ids)) \
        .select_related('Compartmentsvg') \
        .values_list('compartmentsvg__display_name', 'reaction_id')

    else:
        try:
            compartment = APImodels.CompartmentSvg.objects.using(model).get(name__iexact=compartment_name)
            compartmentID = compartment.compartment
        except APImodels.CompartmentSvg.DoesNotExist:
            return HttpResponse(status=404)

        # get the component ids in the input compartment
        rcci = APImodels.ReactionComponentCompartmentSvg.objects.using(model).filter(
                Q(rc_id__in=reaction_component_ids) & Q(Compartmentsvg_id=compartmentID)
            ).select_related('Compartmentsvg') \
            .values_list('compartmentsvg__display_name', 'rc_id')

        # get the reaction ids in the input compartment
        rci = APImodels.ReactionCompartmentSvg.objects.using(model).filter(
            Q(reaction_id__in=reaction_ids) & Q(Compartmentsvg_id=compartmentID)
        ).select_related('Compartmentsvg') \
        .values_list('compartmentsvg__display_name', 'reaction_id')

        if not rcci.count() and not rci.count():
            return HttpResponse(status=404)

    results = reactionComponents = list(chain(rcci, rci))
    return JSONResponse(results)


@api_view()
@is_model_valid
def get_subsystem_coordinates(request, model, subsystem_name, compartment_name=False):
    """
    For a given subsystem name, get the compartment name and X,Y locations in the corresponding SVG map.
    """

    logging.warn(subsystem_name)

    try:
        subsystem = APImodels.Subsystem.objects.using(model).get(name__iexact=subsystem_name)
        subsystem_id = subsystem.id
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    try:
        if not compartment_name:
            tileSubsystem = APImodels.TileSubsystem.objects.using(model).get(subsystem=subsystem_id, is_main=True)
        else:
            try:
                compartment = APImodels.CompartmentSvg.objects.using(model).get(name__iexact=compartment_name)
            except CompartmentSvg.DoesNotExist:
                return HttpResponse(status=404)
            tileSubsystem = APImodels.TileSubsystem.objects.using(model).get(subsystem_id=subsystem_id, compartment=compartment)

    except APImodels.TileSubsystem.DoesNotExist:
        return HttpResponse(status=404)
    serializer = TileSubsystemSerializer(tileSubsystem)

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_db_json(request, model, component_name=None, ctype=None, dup_meta=False):
    if component_name:
        if ctype == 'compartment':
            try:
                compartment = APImodels.Compartment.objects.using(model).get(name__iexact=component_name)
            except Subsystem.DoesNotExist:
                return HttpResponse(status=404)

            reactions_id = APImodels.ReactionCompartment.objects.using(model). \
                filter(compartment=compartment).values_list('reaction', flat=True)
            reactions = APImodels.Reaction.objects.using(model).filter(id__in=reactions_id). \
                prefetch_related('reactants', 'products', 'modifiers')
        else:
            try:
                subsystem = APImodels.Subsystem.objects.using(model).get(name__iexact=component_name)
            except Subsystem.DoesNotExist:
                return HttpResponse(status=404)

            reactions_id = APImodels.SubsystemReaction.objects.using(model). \
                filter(subsystem=subsystem).values_list('reaction', flat=True)
            reactions = APImodels.Reaction.objects.using(model).filter(id__in=reactions_id). \
                prefetch_related('reactants', 'products', 'modifiers')
    else:
        reactions = APImodels.Reaction.objects.using(model).all().prefetch_related('reactants', 'products', 'modifiers')

    nodes = {}
    links = {}
    linksList = []

    duplicateEnzyme = True
    duplicatedEnz= {}
    duplicateMetabolite = dup_meta
    duplicatedId = {}

    duplicateMetaName = {'ATP', 'ADP', 'Pi', 'PPi', 'H2O', 'O2', 'PI pool', 'H+', \
     'NADP', 'NADP+', 'NADH', 'NAD+', 'CoA', 'NADPH', 'acetyl-CoA', 'FAD', 'FADH'}

    for r in reactions:
        reaction = {
            'g': 'r',
            'id': r.id,
            'n': r.id,
        }
        nodes[r.id] = reaction;

        for m in r.reactants.all():
            duplicateCurrentMeta = m.name in duplicateMetaName

            doMeta = True;
            metabolite = None;
            mid = m.id
            if duplicateMetabolite:
                if mid not in nodes:
                    duplicatedId[mid] = 0
                elif duplicateCurrentMeta:
                    duplicatedId[m.id] += 1
                    mid = "%s-%s" % (m.id, duplicatedId[m.id])
                else:
                    doMeta = False;

            if doMeta:
                metabolite = {
                    'g': 'm',
                    'id': mid,
                    # 'rid': m.id,
                    'n': m.name or m.alt_name1,
                }

                nodes[mid] = metabolite;

            rel = {
              #'id': mid + "-" + r.id,
              's': mid,
              't': r.id,
              #'g': 'fe',
              # 'rev': r.is_reversible,
            }
            # links[rel['id']] = rel
            linksList.append(rel)

        for m in r.products.all():
            duplicateCurrentMeta = m.name in duplicateMetaName

            doMeta = True;
            metabolite = None
            mid = m.id;
            if duplicateMetabolite:
                if mid not in nodes:
                    duplicatedId[mid] = 0
                elif duplicateCurrentMeta:
                    duplicatedId[m.id] += 1
                    mid = "%s-%s" % (m.id, duplicatedId[m.id])
                else:
                    doMeta = False

            if doMeta:
                metabolite = {
                    'g': 'm',
                    'id': mid,
                    #'rid': m.id,
                    'n': m.name or m.alt_name1,
                }

                nodes[mid] = metabolite

            rel = {
              #'id': r.id + "-" + mid,
              's': r.id,
              't': mid,
              #'g': 'fe',
              # 'rev': r.is_reversible,
            }
            # links[rel['id']] = rel
            linksList.append(rel)

        for e in r.modifiers.all():
            eid = e.id;
            if eid in nodes:
                duplicatedEnz[eid] += 1;
                eid = "%s-%s" % (eid, duplicatedEnz[eid])
            else:
                duplicatedEnz[eid] = 0;

            enzyme = {
              'id': eid,
              'g': 'e',
              'n': e.name or e.alt_name1,
            }
            nodes[eid] = enzyme;

            rel = {
              #'id': eid + "-" + r.id,
              's': eid,
              't': r.id,
              #'g': 'ee',
              # 'rev': r.is_reversible,
            }
            # links[rel['id']] = rel
            linksList.append(rel)

    results = {
        'nodes': [v for k, v in nodes.items()],
        # 'links': [v for k, v in links.items()],
        'links': linksList
    }

    return JSONResponse(results)


#####################################################################################

@api_view(['POST'])
def get_HPA_xml_content(request):
    url = request.data['url']
    r = requests.get(url)
    if not r.status_code == 200:
        return HttpResponse(status=r.status_code)

    import gzip
    ddata = gzip.decompress(r.content)

    return HttpResponse(ddata)

@api_view()
def HPA_enzyme_info(request, ensembl_id):
    try:
        res = APImodels.ReactionComponent.objects.using('hmr2').get(id=ensembl_id)
        rcid = res.id
    except:
        return JSONResponse([])

    subs = APImodels.Subsystem.objects.using('hmr2').filter(
            Q(id__in=APImodels.SubsystemEnzyme.objects.using('hmr2').filter(rc_id=rcid).values('subsystem_id')) &
            ~Q(system='Collection of reactions')
        ).values('id', 'name', 'reaction_count', 'enzyme_count', 'metabolite_count', 'unique_metabolite_count')

    result = []
    for sub in subs.all():
        # get the reactions
        reactions = APImodels.SubsystemReaction.objects.using('hmr2').filter(subsystem_id=sub['id']).values('reaction_id')
        compartments = APImodels.Compartment.objects.using('hmr2').filter(
            id__in=APImodels.SubsystemCompartment.objects.using('hmr2').filter(subsystem_id=sub['id']).values('compartment_id').distinct()
        ).values_list('name', flat=True)
        sub['compartments'] = list(compartments)
        sub['reactions_catalysed'] = APImodels.ReactionModifier.objects.using('hmr2').filter(Q(reaction__in=reactions) & Q(modifier_id=rcid)).count()
        del sub['id']
        result.append(sub)

    return JSONResponse(result)


#########################################################################################

@api_view()
@is_model_valid
def get_compartment_svg(request, model, compartment_name):
    try:
        compartment = APImodels.CompartmentSvg.objects.using(model).get(display_name__iexact=compartment_name)
    except APImodels.CompartmentSvg.DoesNotExist:
        return HttpResponse(status=404)

    serializer = APIserializer.CompartmentSvgSerializer(compartment)

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_compartments_svg(request, model):
    # TODO put in private url?
    try:
        compartment_svg_info = APImodels.CompartmentSvg.objects.using(model).select_related('compartment').all()
        compartment_info = APImodels.Compartment.objects.using(model).all()
    except APImodels.CompartmentSvg.DoesNotExist:
        return HttpResponse(status=404)

    compartmentSvgSerializer = APIserializer.CompartmentSvgSerializer(compartment_svg_info, many=True)

    # get stats from Compartment and replace it
    compartmentSerializer = APIserializer.CompartmentSerializer(compartment_info, many=True)
    d = {}
    for el in compartmentSerializer.data:
        d[el['name']] = el

    for el in compartmentSvgSerializer.data:
        values = d[el['compartment']]
        el['reaction_count'] = values['reaction_count']
        el['metabolite_count'] = values['metabolite_count']
        el['enzyme_count'] = values['enzyme_count']
        el['subsystem_count'] = values['subsystem_count']

    return JSONResponse(compartmentSvgSerializer.data)

##########################################################################################


@api_view()
@is_model_valid
def get_component_with_interaction_partners(request, model, id):
    """
    Get the annotation + interaction partners for a given reaction component,
    supply an id (for example M_m01954g or E_3640)
    """
    try:
        component = APImodels.ReactionComponent.objects.using(model).get(Q(id__iexact=id) | Q(name__iexact=id))
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    if (component.component_type == 'e'):
        RCSerializerClass = componentDBserializerSelector(model, 'enzyme')
    else:
        RCSerializerClass = componentDBserializerSelector(model, 'metabolite')

    component_serializer = RCSerializerClass(component, context={'model': model})
    reactions_count = component.reactions_as_reactant.count() + \
            component.reactions_as_product.count() + \
            component.reactions_as_modifier.count()

    if reactions_count > 100:
        return HttpResponse(status=406)

    reactions = list(chain(
        component.reactions_as_reactant. \
        prefetch_related('reactants', 'products', 'modifiers', 'reactants__enzyme', 'reactants__metabolite', \
            'products__enzyme', 'products__metabolite', 'modifiers__enzyme', 'modifiers__metabolite', \
            'reactants__compartment', 'products__compartment', 'modifiers__compartment').all(),
        component.reactions_as_product. \
        prefetch_related('reactants', 'products', 'modifiers', 'reactants__enzyme', 'reactants__metabolite', \
            'products__enzyme', 'products__metabolite', 'modifiers__enzyme', 'modifiers__metabolite', \
            'reactants__compartment', 'products__compartment', 'modifiers__compartment').all(),
        component.reactions_as_modifier. \
        prefetch_related('reactants', 'products', 'modifiers', 'reactants__enzyme', 'reactants__metabolite', \
            'products__enzyme', 'products__metabolite', 'modifiers__enzyme', 'modifiers__metabolite', \
            'reactants__compartment', 'products__compartment', 'modifiers__compartment').all()
    ))
    InteractionPartnerSerializerClass = componentDBserializerSelector(model, 'interaction partner')
    reactions_serializer = InteractionPartnerSerializerClass(reactions, many=True)

    result = {
                 'component': component_serializer.data,
                 'reactions': reactions_serializer.data
             }

    return JSONResponse(result)


@api_view()
@is_model_valid
def connected_metabolites(request, model, id):
    try:
        enzyme = APImodels.ReactionComponent.objects.using(model).get(
                Q(component_type='e') &
                (Q(id=id) | Q(name=id))
            )
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    reactions = APImodels.Reaction.objects.using(model).filter(
            Q(reactionmodifier__modifier_id=enzyme.id)
            ).prefetch_related('reactants', 'products', 'modifiers').distinct()

    ReactionSerializerClass = componentDBserializerSelector(model, 'reaction', serializer_type='lite')
    EnzymeSerializerClass = componentDBserializerSelector(model, 'enzyme')

    result =  {
        'enzyme' : EnzymeSerializerClass(enzyme, context={'model': model}).data,
        'reactions': ReactionSerializerClass(reactions, many=True, context={'model': model}).data
    }

    return JSONResponse(result)


##########################################################################################

@api_view()
@is_model_valid
def get_rna_levels(request, model, compartment):
    try:
        compartment = APImodels.Compartment.objects.using(model).get(name__iexact=compartment)
    except APImodels.Compartment.DoesNotExist:
        return HttpResponse(status=404)

    rc_compart = APImodels.ReactionComponentCompartment.objects.using(model). \
        filter(Q(compartment=compartment)).values_list('rc_id')
    enzyme_compart = APImodels.ReactionComponent.objects.using(model). \
        filter(Q(component_type='e') & Q(id__in=rc_compart)).values_list('id')

    levels = APImodels.HpaEnzymeLevel.objects.using(model).filter(rc__in=enzyme_compart).values_list('rc_id', 'levels')
    tissues = APImodels.HpaTissue.objects.using(model).all().values_list('tissue', flat=True)

    return JSONResponse(
        { 
          'tissues': tissues,
          'levels': levels
        })
