from django.conf.urls import url
from api import private_views
from api import views

app_name = 'private_apis'
urlpatterns = [
    url(r'^hpa/enzyme/(?P<ensembl_id>[^/]+)/?$', private_views.HPA_enzyme_info),
    url(r'^hpa/enzymes/$', private_views.HPA_all_enzymes),

    url(r'^(?P<model>[^/]+)/convert_to_reaction_component_ids/(?P<compartment_name_id>[^/]+)/?$', private_views.convert_to_reaction_component_ids),
    url(r'^(?P<model>[^/]+)/convert_to_reaction_component_ids/?$', private_views.convert_to_reaction_component_ids),

    url(r'^(?P<model>[^/]+)/search_map/(?P<map_type>[^/]+)/(?P<map_name_id>[^/]+)/(?P<term>[^/]+)/?$', private_views.search_on_map),
    url(r'^(?P<model>[^/]+)/available_maps/(?P<reaction_id>[^/]+)/?$', private_views.get_available_maps),

    url(r'^(?P<model>[^/]+)/json/?$', private_views.get_db_json),
    url(r'^(?P<model>[^/]+)/json/compartment/(?P<component_name_id>[^/]+)/?$', private_views.get_db_json, {'ctype': 'compartment'}),
    url(r'^(?P<model>[^/]+)/json/subsystem/(?P<component_name_id>[^/]+)/?$', private_views.get_db_json, {'ctype': 'subsystem'}),
    url(r'^(?P<model>[^/]+)/json/compartment/(?P<component_name_id>[^/]+)/duplicate/?$', private_views.get_db_json, {'ctype': 'compartment', 'dup_meta': True}),
    url(r'^(?P<model>[^/]+)/json/subsystem/(?P<component_name_id>[^/]+)/duplicate/?$', private_views.get_db_json, {'ctype': 'subsystem', 'dup_meta': True}),

    url(r'^(?P<model>[^/]+)/reaction_components/(?P<id>[^/]+)/with_interaction_partners/?$', private_views.get_component_with_interaction_partners),
    # url(r'^(?P<model>[^/]+)/compartments_svg/?$', private_views.get_compartments_svg),
    # url(r'^(?P<model>[^/]+)/subsystems_svg/?$', private_views.get_subsystems_svg),
    url(r'^(?P<model>[^/]+)/viewer/?$', private_views.get_data_viewer),

    url(r'^(?P<model>[^/]+)/enzyme/(?P<id>[^/]+)/connected_metabolites/?$', private_views.connected_metabolites),

    url(r'^(?P<model>[^/]+)/enzyme/hpa_rna_levels/(?P<compartment_name_id>[^/]+)/?$', private_views.get_hpa_rna_levels_compartment),
    url(r'^(?P<model>[^/]+)/enzyme/hpa_rna_levels/?$', private_views.get_hpa_rna_levels),
    url(r'^(?P<model>[^/]+)/enzyme/hpa_tissue/?$', private_views.get_hpa_tissues),

    url(r'^(?P<model>[^/]+)/compartment/(?P<compartment_name_id>[^/]+)/stats/?$', views.get_compartment, {'stats_only': True}),
]
