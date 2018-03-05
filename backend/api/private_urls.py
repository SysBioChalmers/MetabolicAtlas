from django.conf.urls import url
from api import views

app_name = 'private_apis'
urlpatterns = [
    url(r'^(?P<model>[^/]+)/convert_to_reaction_component_ids/(?P<compartment_name>[^/]+)/?$', views.convert_to_reaction_component_ids),
    url(r'^(?P<model>[^/]+)/convert_to_reaction_component_ids/?$', views.convert_to_reaction_component_ids),
    url(r'^(?P<model>[^/]+)/showsubsystem/(?P<subsystem_name>[^/]+)/(?P<compartment_name>[^/]+)/?$', views.get_subsystem_coordinates),
    url(r'^(?P<model>[^/]+)/showsubsystem/(?P<subsystem_name>[^/]+)/?$', views.get_subsystem_coordinates),
    url(r'^hpa/xml_request?$', views.get_HPA_xml_content, name="test_url_exclude"),
    url(r'^hpa/enzyme/(?P<ensembl_id>[^/]+)?$', views.HPA_enzyme_info),
]