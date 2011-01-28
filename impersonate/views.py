from django.conf import settings
from django.db.models import Q
from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render_to_response
from decorators import allowed_user_required
from helpers import get_redir_path, get_paginator, check_allow_for_user


@allowed_user_required
def impersonate(request, uid):
    ''' Takes in the UID of the user to impersonate.
        View will fetch the User instance and store it 
        in the request.session under the '_impersonate' key.
        
        The middleware will then pick up on it and adjust the 
        request object as needed.
    '''
    new_user = get_object_or_404(User, pk=uid)
    if check_allow_for_user(request.user, new_user):
        request.session['_impersonate'] = new_user
        request.session.modified = True  # Let's make sure...
    return redirect(get_redir_path())


def stop_impersonate(request):
    ''' Remove the impersonation object from the session
    '''
    if '_impersonate' in request.session:
        del request.session['_impersonate']
        request.session.modified = True
    return redirect(get_redir_path())


@allowed_user_required
def list_users(request, template):
    ''' List all users in the system.
        Will add 4 items to the context.
          * users - queryset of all users
          * paginator - Django Paginator instance
          * page - Current page of objects (from Paginator)
          * page_number - Current page number, defaults to 1
    '''
    users = User.objects.all()
    paginator, page, page_number = get_paginator(request, users)

    return render_to_response(template, {
        'users': users,
        'paginator': paginator,
        'page': page,
        'page_number': page_number,
    }, context_instance=RequestContext(request))


@allowed_user_required
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
    paginator, page, page_number = get_paginator(request, users)

    return render_to_response(template, {
        'users': users,
        'paginator': paginator,
        'page': page,
        'page_number': page_number,
        'query': query,
    }, context_instance=RequestContext(request))
