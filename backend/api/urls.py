from django.conf.urls import url
from api import views

app_name = 'public_apis'
urlpatterns = [
    url(r'^models/?$', views.get_models),
    url(r'^models/(?P<model_id>[^/]+)/?$', views.get_model),
    url(r'^gems/?$', views.get_gemodels),
    url(r'^gems/(?P<gem_id>[^/]+)/?$', views.get_gemodel),
    url(r'^(?P<model>[^/]+)/reactions/?$', views.get_reactions),
    url(r'^(?P<model>[^/]+)/reactions/(?P<id>[^/]+)/?$', views.get_reaction),
    url(r'^(?P<model>[^/]+)/reactions/(?P<id>[^/]+)/reactants/?$', views.get_reaction_reactants),
    # url(r'^(?P<model>[^/]+)/reactions/(?P<reaction_id>[^/]+)/reactants/(?P<reactant_id>[^/]+)/?$', views.get_reaction_reactant),
    url(r'^(?P<model>[^/]+)/reactions/(?P<id>[^/]+)/products/?$', views.get_reaction_products),
    # url(r'^(?P<model>[^/]+)/reactions/(?P<reaction_id>[^/]+)/products/(?P<product_id>[^/]+)/?$', views.get_reaction_product),
    url(r'^(?P<model>[^/]+)/reactions/(?P<id>[^/]+)/modifiers/?$', views.get_reaction_modifiers),
    # url(r'^(?P<model>[^/]+)/reactions/(?P<reaction_id>[^/]+)/modifiers/(?P<modifier_id>[^/]+)/?$', views.get_reaction_modifier),

    # url(r'^(?P<model>[^/]+)/reaction_components/?$', views.component_list),
    # url(r'^(?P<model>[^/]+)/reaction_components/(?P<id>[^/]+)/?$', views.get_component),
    # url(r'^(?P<model>[^/]+)/reaction_components/(?P<id>[^/]+)/currency_metabolites/?$', views.currency_metabolite_list),
    # url(r'^(?P<model>[^/]+)/reaction_components/(?P<id>[^/]+)/interaction_partners/?$', views.interaction_partner_list),

    url(r'^(?P<model>[^/]+)/enzymes/?$', views.get_enzymes),
    url(r'^(?P<model>[^/]+)/enzymes/(?P<id>[^/]+)?$', views.get_enzyme),
    url(r'^(?P<model>[^/]+)/enzymes/(?P<id>[^/]+)/interaction_partners/?$', views.get_enzyme_interaction_partners),
    url(r'^(?P<model>[^/]+)/enzymes/(?P<id>[^/]+)/reactions/?$', views.get_enzyme_reactions),

    url(r'^(?P<model>[^/]+)/metabolites/?$', views.get_metabolites),
    url(r'^(?P<model>[^/]+)/metabolites/(?P<id>[^/]+)/?$', views.get_metabolite),
    url(r'^(?P<model>[^/]+)/metabolites/(?P<id>[^/]+)/interaction_partners/?$', views.get_metabolite_interaction_partners),
    url(r'^(?P<model>[^/]+)/metabolites/(?P<id>[^/]+)/reactions/?$', views.get_metabolite_reactions, {'all_compartment': False }),
    url(r'^(?P<model>[^/]+)/metabolites/(?P<id>[^/]+)/reactions/all_compartment/?$', views.get_metabolite_reactions, {'all_compartment': True}),
    # url(r'^(?P<model>[^/]+)/metabolite_reactions/(?P<id>[^/]+)/reactome/(?P<reaction_id>[^/]+)/?$', views.get_metabolite_reactome),

    url(r'^(?P<model>[^/]+)/subsystems/?$', views.get_subsystems),
    url(r'^(?P<model>[^/]+)/subsystems/(?P<subsystem_name>[^/]+)/?$', views.get_subsystem),
    url(r'^(?P<model>[^/]+)/compartments/?$', views.get_compartments),
    url(r'^(?P<model>[^/]+)/compartments/(?P<compartment_name>[^/]+)/?$', views.get_compartment),

    url(r'^(?P<model>[^/]+)/search/(?P<term>[^/]+)/?$', views.search),

]