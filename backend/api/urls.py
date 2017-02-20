from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^models/?$', views.model_list),
    url(r'^models/(?P<id>[0-9]+)/?$', views.get_model),
    url(r'^authors/?$', views.author_list),
    url(r'^authors/(?P<id>[0-9]+)/?$', views.get_author),
    url(r'^reactions/?$', views.reaction_list),
    url(r'^reactions/(?P<id>[^/]+)/?$', views.get_reaction),
    url(r'^reactions/(?P<id>[^/]+)/reactants/?$', views.reaction_reactant_list),
    url(r'^reactions/(?P<reaction_id>[^/]+)/reactants/(?P<reactant_id>[^/]+)/?$', views.get_reaction_reactant),
    url(r'^reactions/(?P<id>[^/]+)/products/?$', views.reaction_product_list),
    url(r'^reactions/(?P<reaction_id>[^/]+)/products/(?P<product_id>[^/]+)/?$', views.get_reaction_product),
    url(r'^reactions/(?P<id>[^/]+)/modifiers/?$', views.reaction_modifier_list),
    url(r'^reactions/(?P<reaction_id>[^/]+)/modifiers/(?P<modifier_id>[^/]+)/?$', views.get_reaction_modifier),
    url(r'^reaction_components/?$', views.component_list),
]
