from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect


def _get_redir_path():
    return getattr(
        settings,
        'IMPERSONATE_REDIRECT_URL',
        getattr(settings, 'LOGIN_REDIRECT_URL', '/'),
    )


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
