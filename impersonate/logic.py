from django.conf import settings

from .helpers import check_allow_for_user, get_redir_path
from .signals import session_begin, session_end


def impersonate(request, new_user):
    if check_allow_for_user(request, new_user):
        request.session['_impersonate'] = new_user.id
        prev_path = request.META.get('HTTP_REFERER')
        if prev_path:
            request.session['_impersonate_prev_path'] = \
                                request.build_absolute_uri(prev_path)

        request.session.modified = True  # Let's make sure...
        # can be used to hook up auditing of the session
        session_begin.send(
            sender=None,
            impersonator=request.user,
            impersonating=new_user,
            request=request
        )


def stop_impersonate(request):
    if '_impersonate' in request.session:
        # modify request.user before popping _impersonate to trigger
        # apply_impersonate with the correct state
        request.session.modified = True
        request.user.is_impersonate = False
        request.user = request.impersonator

        impersonating = request.session.pop('_impersonate', None)

        session_end.send(
            sender=None,
            impersonator=request.impersonator,
            impersonating=impersonating,
            request=request
        )

    original_path = request.session.pop('_impersonate_prev_path', None)
    use_refer = getattr(settings, 'IMPERSONATE_USE_HTTP_REFERER', False)
    dest = original_path \
        if original_path and use_refer else get_redir_path(request)
    return dest
