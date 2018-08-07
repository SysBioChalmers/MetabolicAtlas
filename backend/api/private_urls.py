from django.conf.urls import url
from api import private_views

app_name = 'private_apis'
urlpatterns = [
    url(r'^(?P<model>[^/]+)/convert_to_reaction_component_ids/(?P<compartment_name>[^/]+)/?$', private_views.convert_to_reaction_component_ids),
    url(r'^(?P<model>[^/]+)/convert_to_reaction_component_ids/?$', private_views.convert_to_reaction_component_ids),
    url(r'^(?P<model>[^/]+)/subsystem_coord/(?P<subsystem_name>[^/]+)/(?P<compartment_name>[^/]+)/?$', private_views.get_subsystem_coordinates),
    url(r'^(?P<model>[^/]+)/subsystem_coord/(?P<subsystem_name>[^/]+)/?$', private_views.get_subsystem_coordinates),

    url(r'^hpa/xml_request?$', private_views.get_HPA_xml_content),
    url(r'^hpa/enzyme/(?P<ensembl_id>[^/]+)?$', private_views.HPA_enzyme_info),

    url(r'^(?P<model>[^/]+)/json/?$', private_views.get_db_json),
    url(r'^(?P<model>[^/]+)/json/compartment/(?P<component_name>[^/]+)/?$', private_views.get_db_json, {'ctype': 'compartment'}),
    url(r'^(?P<model>[^/]+)/json/subsystem/(?P<component_name>[^/]+)/?$', private_views.get_db_json, {'ctype': 'subsystem'}),
    url(r'^(?P<model>[^/]+)/json/compartment/(?P<component_name>[^/]+)/duplicate/?$', private_views.get_db_json, {'ctype': 'compartment', 'dup_meta': True}),
    url(r'^(?P<model>[^/]+)/json/subsystem/(?P<component_name>[^/]+)//duplicate/?$', private_views.get_db_json, {'ctype': 'subsystem', 'dup_meta': True}),

    url(r'^(?P<model>[^/]+)/reaction_components/(?P<id>[^/]+)/with_interaction_partners/?$', private_views.get_component_with_interaction_partners),
    url(r'^(?P<model>[^/]+)/compartments_svg/?$', private_views.get_compartments_svg),
    url(r'^(?P<model>[^/]+)/enzymes/(?P<id>[^/]+)/connected_metabolites/?$', private_views.connected_metabolites),

    url(r'^(?P<model>[^/]+)/enzymes/hparnalevels/(?P<compartment>[^/]+)/?$', private_views.get_rna_levels),
]