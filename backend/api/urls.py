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
]
