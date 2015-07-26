from django.conf import settings
from django.db.models import Q

from .helpers import (get_paginator, get_redir_arg, get_redir_field,
                      users_impersonable)

try:
    # Django 1.5 check
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()


def get_list_template_context(request):
    ''' List all users in the system.
        Will add 5 items to the context.
          * users - queryset of all users
          * paginator - Django Paginator instance
          * page - Current page of objects (from Paginator)
          * page_number - Current page number, defaults to 1
          * redirect - arg for redirect target, e.g. "?next=/foo/bar"
    '''
    users = users_impersonable(request)

    paginator, page, page_number = get_paginator(request, users)

    return {
        'users': users,
        'paginator': paginator,
        'page': page,
        'page_number': page_number,
        'redirect': get_redir_arg(request),
        'redirect_field': get_redir_field(request),
    }


def get_search_template_context(request, query):
    ''' Simple search through the users.
        Will add 7 items to the context.
          * users - All users that match the query passed.
          * paginator - Django Paginator instance
          * page - Current page of objects (from Paginator)
          * page_number - Current page number, defaults to 1
          * query - The search query that was entered
          * redirect - arg for redirect target, e.g. "?next=/foo/bar"
          * redirect_field - hidden input field with redirect argument,
                              put this inside search form
    '''

    # get username field
    username_field = getattr(User, 'USERNAME_FIELD', 'username')

    # define search fields and lookup type
    search_fields = set(getattr(settings, 'IMPERSONATE_SEARCH_FIELDS',
                        [username_field, 'first_name', 'last_name', 'email']))
    lookup_type = getattr(settings, 'IMPERSONATE_LOOKUP_TYPE', 'icontains')

    # prepare kwargs
    search_q = Q()
    for term in query.split():
        sub_q = Q()
        for search_field in search_fields:
            sub_q |= Q(**{'{0}__{1}'.format(search_field, lookup_type): term})
        search_q &= sub_q

    users = users_impersonable(request)
    users = users.filter(search_q)
    paginator, page, page_number = get_paginator(request, users)

    return {
        'users': users,
        'paginator': paginator,
        'page': page,
        'page_number': page_number,
        'query': query,
        'redirect': get_redir_arg(request),
        'redirect_field': get_redir_field(request),
    }
