from django.conf.urls import url

from .views import impersonate, list_users, search_users, stop_impersonate

try:
    # Django <=1.9
    from django.conf.urls import patterns
except ImportError:
    patterns = None

urlpatterns = [
    url(r'^stop/$',
        stop_impersonate,
        name='impersonate-stop'),
    url(r'^list/$',
        list_users,
        {'template': 'impersonate/list_users.html'},
        name='impersonate-list'),
    url(r'^search/$',
        search_users,
        {'template': 'impersonate/search_users.html'},
        name='impersonate-search'),
    url(r'^(?P<uid>.+)/$',
        impersonate,
        name='impersonate-start'),
]

if patterns is not None:
    urlpatterns = patterns('', *urlpatterns)
