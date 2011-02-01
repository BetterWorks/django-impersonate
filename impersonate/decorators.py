from django.conf import settings
from django.shortcuts import redirect
from django.utils.http import urlquote
from django.contrib.auth import REDIRECT_FIELD_NAME
from helpers import get_redir_path, check_allow_staff


def allowed_user_required(view_func):
    def _checkuser(request, *args, **kwargs):
        allow_staff = check_allow_staff()
        if not request.user.is_authenticated():
            return redirect('%s?%s=%s' % (
                settings.LOGIN_URL,
                REDIRECT_FIELD_NAME,
                urlquote(request.get_full_path()),
            ))

        if getattr(request.user, 'is_impersonate', False):
            # Do not allow an impersonated session to use the 
            # impersonate views.
            return redirect(get_redir_path())

        if not request.user.is_superuser:
            if not request.user.is_staff or not allow_staff:
                return redirect(get_redir_path())

        return view_func(request, *args, **kwargs)
    return _checkuser
