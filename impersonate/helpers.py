from django.conf import settings
from django.core.paginator import Paginator, EmptyPage

 
def get_redir_path():        
    return getattr(
        settings,
        'IMPERSONATE_REDIRECT_URL',
        getattr(settings, 'LOGIN_REDIRECT_URL', '/'),
    )       
        
    
def get_paginator(request, qs):
    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        page_number = 1

    paginator = Paginator(
        qs,
        int(getattr(settings, 'IMPERSONATE_PAGINATE_COUNT', 20)),
    )   
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = None

    return (paginator, page, page_number)


def check_allow_staff():
    return (not getattr(settings, 'IMPERSONATE_REQUIRE_SUPERUSER', False))


def check_allow_for_user(start_user, end_user):
    if not start_user.is_superuser:
        allow_staff = check_allow_staff()
        if start_user.is_staff and allow_staff:
            if not end_user.is_superuser:
                return True
    else:
        return True

    return False
