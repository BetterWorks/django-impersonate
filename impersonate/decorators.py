import django
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from urllib.parse import quote

from .helpers import check_allow_impersonate, get_redir_path


def get_login_url():
    # support named URL patterns from Django 1.5 onwards
    if django.VERSION >= (1, 5):
        from django.shortcuts import resolve_url
        from django.utils.encoding import force_str

        return force_str(resolve_url(settings.LOGIN_URL))
    else:
        return settings.LOGIN_URL


def allowed_user_required(view_func):
    def _checkuser(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(u'{0}?{1}={2}'.format(
                get_login_url(),
                REDIRECT_FIELD_NAME,
                quote(request.get_full_path()),
            ))

        if check_allow_impersonate(request):
            # user is allowed to impersonate
            return view_func(request, *args, **kwargs)
        else:
            # user not allowed impersonate at all
            return redirect(get_redir_path())

    return _checkuser
