from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^stop/$', views.stop_impersonate, name='impersonate-stop'),
    url(r'^list/$', views.list_users, name='impersonate-list'),
    url(r'^search/$', views.search_users, name='impersonate-search'),
    url(r'^(?P<uid>.+)/$', views.impersonate, name='impersonate-start'),
]
