from django.conf import settings
from django.db.models import Q
from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import get_object_or_404, redirect, render_to_response


def _get_redir_path():
    return getattr(
        settings,
        'IMPERSONATE_REDIRECT_URL',
        getattr(settings, 'LOGIN_REDIRECT_URL', '/'),
    )


def _get_paginator(request, qs):
    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        page_number = 1

    paginator = Paginator(qs, 20)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = None

    return (paginator, page, page_number)


def impersonate(request, uid):
    ''' Takes in the UID of the user to impersonate.
        View will fetch the User instance and store it 
        in the request.session under the '_impersonate' key.
        
        The middleware will then pick up on it and adjust the 
        request object as needed.
    '''
    new_user = get_object_or_404(User, pk=uid)
    request.session['_impersonate'] = new_user
    request.session.modified = True  # Let's make sure...
    return redirect(_get_redir_path())


def stop_impersonate(request):
    ''' Remove the impersonation object from the session
    '''
    if '_impersonate' in request.session:
        del request.session['_impersonate']
        request.session.modified = True
    return redirect(_get_redir_path())


def list_users(request, template):
    ''' List all users in the system.
        Will add 4 items to the context.
          * users - queryset of all users
          * paginator - Django Paginator instance
          * page - Current page of objects (from Paginator)
          * page_number - Current page number, defaults to 1
    '''
    users = User.objects.all()
    paginator, page, page_number = _get_paginator(request, users)

    return render_to_response(template, {
        'users': users,
        'paginator': paginator,
        'page': page,
        'page_number': page_number,
    }, context_instance=RequestContext(request))


def search_users(request, template):
    ''' Simple search through the users.
        Will add 5 items to the context.
          * users - All users that match the query passed.
          * paginator - Django Paginator instance
          * page - Current page of objects (from Paginator)
          * page_number - Current page number, defaults to 1
          * query - The search query that was entered
    '''
    query = request.GET.get('q', '')
    search_q = Q(username__icontains=query) | \
               Q(first_name__icontains=query) | \
               Q(last_name__icontains=query) | \
               Q(email__icontains=query)
    users = User.objects.filter(search_q)
    paginator, page, page_number = _get_paginator(request, users)

    return render_to_response(template, {
        'users': users,
        'paginator': paginator,
        'page': page,
        'page_number': page_number,
        'query': query,
    }, context_instance=RequestContext(request))
