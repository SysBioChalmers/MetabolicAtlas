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
def convert_to_reaction_component_ids(request, model, compartment_name_id=None):
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

    if not compartment_name_id:
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
            compartment = APImodels.CompartmentSvg.objects.using(model).get(name_id=compartment_name_id)
            compartmentID = compartment.compartment
        except APImodels.CompartmentSvg.DoesNotExist:
            return HttpResponse(status=404)

        # get the component ids in the input compartment
        rcci = APImodels.ReactionComponentCompartmentSvg.objects.using(model).filter(
                Q(rc_id__in=reaction_component_ids) & Q(Compartmentsvg_id=compartment.id)
            ).select_related('Compartmentsvg') \
            .values_list('compartmentsvg__display_name', 'rc_id')

        # get the reaction ids in the input compartment
        rci = APImodels.ReactionCompartmentSvg.objects.using(model).filter(
            Q(reaction_id__in=reaction_ids) & Q(Compartmentsvg_id=compartment.id)
        ).select_related('Compartmentsvg') \
        .values_list('compartmentsvg__display_name', 'reaction_id')

        if not rcci.count() and not rci.count():
            return HttpResponse(status=404)

    results = reactionComponents = list(chain(rcci, rci))
    return JSONResponse(results)


@api_view()
@is_model_valid
def search_on_map(request, model, map_type, map_name_id, term):
    if not term:
        return JSONResponse([])

    if map_type not in ['subsystem', 'compartment'] or not map_name_id:
        return HttpResponse(status=404)

    query = Q()
    reaction_query = Q()
    query |= Q(id__iexact=term)
    reaction_query |= Q(id__iexact=term)
    query |= Q(name__iexact=term)
    query |= Q(alt_name1__iexact=term)
    query |= Q(alt_name2__iexact=term)
    query |= Q(external_id1__iexact=term)
    query |= Q(external_id2__iexact=term)
    query |= Q(external_id3__iexact=term)
    query |= Q(external_id4__iexact=term)

    mapIDset = None
    if map_type == 'compartment':
        try:
            compartment = APImodels.CompartmentSvg.objects.using(model).get(name_id=map_name_id)
            mapIDsetRC  = APImodels.ReactionComponentCompartmentSvg.objects.using(model) \
                .filter(Q(compartmentsvg=compartment.id)).values_list('rc_id')
            mapIDsetReaction = APImodels.ReactionCompartmentSvg.objects.using(model) \
                .filter(Q(compartmentsvg=compartment.id)).values_list('reaction_id')
        except APImodels.CompartmentSvg.DoesNotExist:
            return HttpResponse(status=404)
    else:
        try:
            subsystem = APImodels.SubsystemSvg.objects.using(model).get(name_id=map_name_id)
            mapIDsetRC  = APImodels.ReactionComponentSubsystemSvg.objects.using(model) \
                .filter(Q(subsystemsvg=subsystem.id)).values_list('rc_id')
            mapIDsetReaction = APImodels.ReactionSubsystemSvg.objects.using(model) \
                .filter(Q(subsystemsvg=subsystem.id)).values_list('reaction_id')
        except APImodels.SubsystemSvg.DoesNotExist:
            return HttpResponse(status=404)

    # get the list of component id
    reaction_component_ids = APImodels.ReactionComponent.objects.using(model).filter(id__in=mapIDsetRC).filter(query).values_list('id', flat=True);

    # get the list of reaction id
    reaction_ids = APImodels.Reaction.objects.using(model).filter(id__in=mapIDsetReaction).filter(reaction_query).values_list('id', flat=True)

    if not reaction_component_ids.count() and not reaction_ids.count():
        return HttpResponse(status=404)

    results = list(chain(reaction_component_ids, reaction_ids))
    return JSONResponse(results)


# @api_view()
# @is_model_valid
# def get_subsystem_coordinates(request, model, subsystem_name, compartment_name=False):
#     """
#     For a given subsystem name, get the compartment name and X,Y locations in the corresponding SVG map.
#     """

#     logging.warn(subsystem_name)

#     try:
#         subsystem = APImodels.Subsystem.objects.using(model).get(name__iexact=subsystem_name)
#         subsystem_id = subsystem.id
#     except APImodels.Subsystem.DoesNotExist:
#         return HttpResponse(status=404)

#     try:
#         if not compartment_name:
#             tileSubsystem = APImodels.TileSubsystem.objects.using(model).get(subsystem=subsystem_id, is_main=True)
#         else:
#             try:
#                 compartment = APImodels.CompartmentSvg.objects.using(model).get(name__iexact=compartment_name)
#             except CompartmentSvg.DoesNotExist:
#                 return HttpResponse(status=404)
#             tileSubsystem = APImodels.TileSubsystem.objects.using(model).get(subsystem_id=subsystem_id, compartment=compartment)

#     except APImodels.TileSubsystem.DoesNotExist:
#         return HttpResponse(status=404)
#     serializer = TileSubsystemSerializer(tileSubsystem)

#     return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_db_json(request, model, component_name_id=None, ctype=None, dup_meta=False):
    if component_name_id:
        if ctype == 'compartment':
            try:
                # TODO fix 'cytosol' request
                compartment = APImodels.Compartment.objects.using(model).get(name_id__iexact=component_name_id)
                # compartment = compartmentSVG.compartment
            except APImodels.Compartment.DoesNotExist:
                return HttpResponse(status=404)

            reactions_id = APImodels.ReactionCompartment.objects.using(model). \
                filter(compartment=compartment).values_list('reaction', flat=True)
            reactions = APImodels.Reaction.objects.using(model).filter(id__in=reactions_id). \
                prefetch_related('reactants', 'products', 'modifiers')
        else:
            try:
                subsystem = APImodels.Subsystem.objects.using(model).get(name_id__iexact=component_name_id)
                # subsystem = subsystemSVG.subsystem
            except APImodels.Subsystem.DoesNotExist:
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

@api_view()
def HPA_all_enzymes(request):
    model = "hmr2"
    result = APImodels.SubsystemEnzyme.objects.using(model).values_list('rc__id', 'subsystem__name','subsystem__name_id')
    return JSONResponse(result)

@api_view()
def HPA_enzyme_info(request, ensembl_id): # ENSG00000110921
    model = "hmr2"
    # TODO provide the model, remove 'hmr2'
    try:
        res = APImodels.ReactionComponent.objects.using(model).get(id=ensembl_id)
        rcid = res.id
    except:
        return HttpResponse(status=404)

    subs = APImodels.Subsystem.objects.using(model).filter(
            Q(id__in=APImodels.SubsystemEnzyme.objects.using(model).filter(rc_id=rcid).values('subsystem_id')) &
            ~Q(system='Collection of reactions')
        ).values('id', 'name', 'name_id', 'reaction_count', 'enzyme_count', 'metabolite_count', 'unique_metabolite_count')

    subsystems = []
    for sub in subs.all():
        # get the reactions
        reactions = APImodels.SubsystemReaction.objects.using(model).filter(subsystem_id=sub['id']).values('reaction_id')
        compartments = APImodels.Compartment.objects.using(model).filter(
            id__in=APImodels.SubsystemCompartment.objects.using(model).filter(subsystem_id=sub['id']).values('compartment_id').distinct()
        ).values_list('name', flat=True)
        sub['enzymes'] = APImodels.SubsystemEnzyme.objects.using(model).filter(subsystem_id=sub['id']).values_list('rc_id', flat=True)
        sub['compartments'] = list(compartments)
        sub['reactions_catalysed'] = APImodels.ReactionModifier.objects.using(model).filter(Q(reaction__in=reactions) & Q(modifier_id=rcid)).count()
        sub['map_url'] = "https://ftp.icsb.chalmers.se/.maps/%s/%s.svg" % (model, sub['name_id'])
        sub['subsystem_url'] = "https://icsb.chalmers.se/explore/gem-browser/%s/subsystem/%s" % (model, sub['name_id'])
        sub['model_metabolite_count'] = sub['unique_metabolite_count']
        sub['compartment_metabolite_count'] = sub['metabolite_count']
        del sub['metabolite_count']
        del sub['unique_metabolite_count']
        del sub['id']
        del sub['name_id']
        subsystems.append(sub)

    result = {
        'enzyme_url': "https://icsb.chalmers.se/explore/gem-browser/%s/enzyme/%s" % (model, ensembl_id),
        'subsystems': subsystems,
        'doc': 'A subsystem can contain the same chemical metabolite that comes from different compartments.',
    }

    return JSONResponse(result)


#########################################################################################

@api_view()
@is_model_valid
def get_compartment_svg(request, model, compartment_name_id):
    try:
        compartment = APImodels.CompartmentSvg.objects.using(model).get(name_id__iexact=compartment_name_id)
    except APImodels.CompartmentSvg.DoesNotExist:
        return HttpResponse(status=404)

    serializer = APIserializer.CompartmentSvgSerializer(compartment)

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_compartments_svg(request, model):
    try:
        compartment_svg_info = APImodels.CompartmentSvg.objects.using(model).select_related('compartment').all()
    except APImodels.CompartmentSvg.DoesNotExist:
        return HttpResponse(status=404)

    compartmentSvgSerializer = APIserializer.CompartmentSvgSerializer(compartment_svg_info, many=True)

    return JSONResponse(compartmentSvgSerializer.data)


@api_view()
@is_model_valid
def get_subsystems_svg(request, model):
    try:
        subsystem_svg_info = APImodels.SubsystemSvg.objects.using(model).select_related('subsystem').all()
    except APImodels.SubsystemSvg.DoesNotExist:
        return HttpResponse(status=404)

    subsystemSvgSerializer = APIserializer.SubsystemSvgSerializer(subsystem_svg_info, many=True)

    return JSONResponse(subsystemSvgSerializer.data)


@api_view()
@is_model_valid
def get_data_viewer(request, model):
    try:
        compartments = APImodels.Compartment.objects.using(model).all()
    except APImodels.Compartment.DoesNotExist:
        return HttpResponse(status=404)

    try:
        compartments_svg = APImodels.CompartmentSvg.objects.using(model).select_related('compartment').all()
    except APImodels.CompartmentSvg.DoesNotExist:
        return HttpResponse(status=404)

    try:
        subsystems = APImodels.Subsystem.objects.using(model).all().prefetch_related('compartment')
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    try:
        subsystems_svg = APImodels.SubsystemSvg.objects.using(model).select_related('subsystem').all()
    except APImodels.SubsystemSvg.DoesNotExist:
        return HttpResponse(status=404)

    return JSONResponse({
            'subsystem': APIserializer.SubsystemSerializer(subsystems, many=True).data,
            'subsystemsvg': APIserializer.SubsystemSvgSerializer(subsystems_svg, many=True).data,
            'compartment':  APIserializer.CompartmentSerializer(compartments, many=True).data,
            'compartmentsvg': APIserializer.CompartmentSvgSerializer(compartments_svg, many=True).data
        })

##########################################################################################

@api_view()
@is_model_valid
def get_tiles_data(request, model):

    # l = logging.getLogger('django.db.backends')
    # l.setLevel(logging.DEBUG)
    # l.addHandler(logging.StreamHandler())

    # TODO optimize the queries or use raw()
    compartments = APImodels.Compartment.objects.using(model).all().order_by('?').prefetch_related('subsystem')[:10]
    subsystems = APImodels.Subsystem.objects.using(model).all().order_by('?')[:10]
    reactions = APImodels.Reaction.objects.using(model).all().order_by('?')[:10]
    metabolites = APImodels.ReactionComponent.objects.using(model).filter(component_type='m').order_by('?')[:10]
    enzymes = APImodels.ReactionComponent.objects.using(model).filter(component_type='e').order_by('?')[:10]
    res = APImodels.GemBrowserTile(compartments, subsystems, reactions, metabolites, enzymes)
    return JSONResponse(APIserializer.GemBrowserTileSerializer(res).data)


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
                (Q(id__iexact=id) | Q(id__iexact=id))
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
def get_hpa_tissues(request, model):
    tissues = APImodels.HpaTissue.objects.using(model).all().values_list('tissue', flat=True)
    return JSONResponse(tissues)


@api_view()
@is_model_valid
def get_hpa_rna_levels_compartment(request, model, compartment_name_id):
    try:
        compartment = APImodels.Compartment.objects.using(model).get(name_id__iexact=compartment_name_id)
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


@api_view(['POST'])
@is_model_valid
def get_hpa_rna_levels(request, model):
    ensemblIDs = [el.strip() for el in request.data['data'] if len(el) != 0]
    if not ensemblIDs:
        return HttpResponse(status=404)

    levels = APImodels.HpaEnzymeLevel.objects.using(model).filter(rc__in=ensemblIDs).values_list('rc_id', 'levels')
    tissues = APImodels.HpaTissue.objects.using(model).all().values_list('tissue', flat=True)

    return JSONResponse(
        {
          'tissues': tissues,
          'levels': levels
        })
