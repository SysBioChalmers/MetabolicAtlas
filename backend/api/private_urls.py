from django.conf.urls import url
from api import views

app_name = 'private_apis'
urlpatterns = [
    url(r'^(?P<model>[^/]+)/convert_to_reaction_component_ids/(?P<compartment_name>[^/]+)/?$', views.convert_to_reaction_component_ids),
    url(r'^(?P<model>[^/]+)/convert_to_reaction_component_ids/?$', views.convert_to_reaction_component_ids),
    url(r'^(?P<model>[^/]+)/subsystem_coord/(?P<subsystem_name>[^/]+)/(?P<compartment_name>[^/]+)/?$', views.get_subsystem_coordinates),
    url(r'^(?P<model>[^/]+)/subsystem_coord/(?P<subsystem_name>[^/]+)/?$', views.get_subsystem_coordinates),
    url(r'^hpa/xml_request?$', views.get_HPA_xml_content, name="test_url_exclude"),
    url(r'^hpa/enzyme/(?P<ensembl_id>[^/]+)?$', views.HPA_enzyme_info),
    url(r'^(?P<model>[^/]+)/json/?$', views.get_db_json),
    url(r'^(?P<model>[^/]+)/json/compartment/(?P<component_name>[^/]+)/?$', views.get_db_json, {'ctype': 'compartment'}),
    url(r'^(?P<model>[^/]+)/json/subsystem/(?P<component_name>[^/]+)/?$', views.get_db_json, {'ctype': 'subsystem'}),
    url(r'^(?P<model>[^/]+)/json/compartment/(?P<component_name>[^/]+)/duplicate/?$', views.get_db_json, {'ctype': 'compartment', 'dup_meta': True}),
    url(r'^(?P<model>[^/]+)/json/subsystem/(?P<component_name>[^/]+)//duplicate/?$', views.get_db_json, {'ctype': 'subsystem', 'dup_meta': True}),
]