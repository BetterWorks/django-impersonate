from django.urls import re_path

from .views import impersonate, list_users, search_users, stop_impersonate


urlpatterns = [
    re_path(r'^stop/$',
        stop_impersonate,
        name='impersonate-stop'),
    re_path(r'^list/$',
        list_users,
        {'template': 'impersonate/list_users.html'},
        name='impersonate-list'),
    re_path(r'^search/$',
        search_users,
        {'template': 'impersonate/search_users.html'},
        name='impersonate-search'),
    re_path(r'^(?P<uid>.+)/$',
        impersonate,
        name='impersonate-start'),
]
