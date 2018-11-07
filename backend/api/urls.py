from django.conf.urls import url
from api import views

app_name = 'public_apis'
urlpatterns = [
    url(r'^models/?$', views.get_models),
    url(r'^models/(?P<model_id>[^/]+)/?$', views.get_model),
    url(r'^gems/?$', views.get_gemodels),
    url(r'^gems/(?P<gem_id>[^/]+)/?$', views.get_gemodel),
    url(r'^(?P<model>[^/]+)/reaction/?$', views.get_reactions),
    url(r'^(?P<model>[^/]+)/reaction/(?P<id>[^/]+)/?$', views.get_reaction),
    url(r'^(?P<model>[^/]+)/reaction/(?P<id>[^/]+)/reactants/?$', views.get_reaction_reactants),
    url(r'^(?P<model>[^/]+)/reaction/(?P<id>[^/]+)/products/?$', views.get_reaction_products),
    url(r'^(?P<model>[^/]+)/reaction/(?P<id>[^/]+)/modifiers/?$', views.get_reaction_modifiers),

    url(r'^(?P<model>[^/]+)/enzyme/?$', views.get_enzymes),
    url(r'^(?P<model>[^/]+)/enzyme/(?P<id>[^/]+)?$', views.get_enzyme),
    url(r'^(?P<model>[^/]+)/enzyme/(?P<id>[^/]+)/interaction_partners/?$', views.get_enzyme_interaction_partners),
    url(r'^(?P<model>[^/]+)/enzyme/(?P<id>[^/]+)/reactions/?$', views.get_enzyme_reactions),

    url(r'^(?P<model>[^/]+)/metabolite/?$', views.get_metabolites),
    url(r'^(?P<model>[^/]+)/metabolite/(?P<id>[^/]+)/?$', views.get_metabolite),
    url(r'^(?P<model>[^/]+)/metabolite/(?P<id>[^/]+)/interaction_partners/?$', views.get_metabolite_interaction_partners),
    url(r'^(?P<model>[^/]+)/metabolite/(?P<id>[^/]+)/reactions/?$', views.get_metabolite_reactions, {'all_compartment': False }),
    url(r'^(?P<model>[^/]+)/metabolite/(?P<id>[^/]+)/reactions/all_compartment/?$', views.get_metabolite_reactions, {'all_compartment': True}),

    url(r'^(?P<model>[^/]+)/subsystem/?$', views.get_subsystems),
    url(r'^(?P<model>[^/]+)/subsystem/(?P<subsystem_name_id>[^/]+)/?$', views.get_subsystem),
    url(r'^(?P<model>[^/]+)/compartment/?$', views.get_compartments),
    url(r'^(?P<model>[^/]+)/compartment/(?P<compartment_name_id>[^/]+)/?$', views.get_compartment),

    url(r'^(?P<model>[^/]+)/search/(?P<term>[^/]+)/?$', views.search),

]