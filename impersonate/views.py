from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import allowed_user_required
from .helpers import (
    get_redir_path, get_redir_arg, get_paginator, get_redir_field,
    check_allow_for_user, users_impersonable
)
from .signals import session_begin, session_end

try:
    # Django 1.5 check
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()


@allowed_user_required
def impersonate(request, uid):
    ''' Takes in the UID of the user to impersonate.
        View will fetch the User instance and store it
        in the request.session under the '_impersonate' key.

        The middleware will then pick up on it and adjust the
        request object as needed.
    '''
    new_user = get_object_or_404(User, pk=uid)
    if check_allow_for_user(request, new_user):
        request.session['_impersonate'] = new_user.id
        request.session.modified = True  # Let's make sure...
        # can be used to hook up auditing of the session
        session_begin.send(
            sender=None,
            impersonator=request.user,
            impersonating=new_user,
            request=request
        )
    return redirect(get_redir_path(request))


def stop_impersonate(request):
    ''' Remove the impersonation object from the session
    '''
    impersonating = request.session.pop('_impersonate', None)
    if impersonating is not None:
        request.session.modified = True
        session_end.send(
            sender=None,
            impersonator=request.impersonator,
            impersonating=impersonating,
            request=request
        )
    return redirect(get_redir_path(request))


@allowed_user_required
def list_users(request, template):
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

    return render(request, template, {
        'users': users,
        'paginator': paginator,
        'page': page,
        'page_number': page_number,
        'redirect': get_redir_arg(request),
        'redirect_field': get_redir_field(request),
    })


@allowed_user_required
def search_users(request, template):
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
    query = request.GET.get('q', '')

    # get username field
    username_field = getattr(User, 'USERNAME_FIELD', 'username')

    # define search fields and lookup type
    search_fields = set(getattr(settings, 'IMPERSONATE_SEARCH_FIELDS',
                            [username_field, 'first_name', 'last_name', 'email']))
    lookup_type = getattr(settings, 'IMPERSONATE_LOOKUP_TYPE', 'icontains')

    # prepare kwargs
    search_q = Q()
    for search_field in search_fields:
        search_q |= Q(**{'{0}__{1}'.format(search_field, lookup_type): query})

    users = users_impersonable(request)
    users = users.filter(search_q)
    paginator, page, page_number = get_paginator(request, users)

    return render(request, template, {
        'users': users,
        'paginator': paginator,
        'page': page,
        'page_number': page_number,
        'query': query,
        'redirect': get_redir_arg(request),
        'redirect_field': get_redir_field(request),
    })
