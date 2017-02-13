from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^model_list/$', views.model_list),
    url(r'^author_list/$', views.author_list),
]
