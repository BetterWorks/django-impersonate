from .helpers import check_allow_for_user
from .signals import session_begin, session_end


def impersonate(request, new_user):
    ''' Takes in the UID of the user to impersonate.
    View will fetch the User instance and store it
    in the request.session under the '_impersonate' key.

    The middleware will then pick up on it and adjust the
    request object as needed.
    '''
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


def stop_impersonate(request):
    ''' Remove the impersonation object from the session
    '''
    impersonating = request.session.pop('_impersonate', None)
    if impersonating is not None:
        request.session.modified = True
        request.user.is_impersonate = False
        request.user = request.impersonator

        session_end.send(
            sender=None,
            impersonator=request.impersonator,
            impersonating=impersonating,
            request=request
        )
