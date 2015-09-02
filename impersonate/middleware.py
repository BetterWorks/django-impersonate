from django.utils.functional import empty, SimpleLazyObject
from .helpers import User, check_allow_for_uri, check_allow_for_user


def apply_impersonate(request):
    request.user.is_impersonate = False
    request.impersonator = None

    if request.user.is_authenticated() and \
       '_impersonate' in request.session:
        new_user_id = request.session['_impersonate']
        if isinstance(new_user_id, User):
            # Edge case for issue 15
            new_user_id = new_user_id.id

        try:
            new_user = User.objects.get(id=new_user_id)
        except User.DoesNotExist:
            return

        if check_allow_for_user(request, new_user) and \
           check_allow_for_uri(request.path):
            request.impersonator = request.user
            request.user = new_user
            request.user.is_impersonate = True


def impersonator(request):
    # Trigger apply_impersonate
    request.user.is_authenticated()

    return request.impersonator


class ImpersonateMiddleware(object):
    def process_request(self, request):
        # User isn't lazy, don't preserve laziness.
        if not isinstance(request.user, SimpleLazyObject):
            apply_impersonate(request)
            return None

        # User is already set up, don't preserve laziness
        if request.user.__dict__['_wrapped'] is not empty:
            apply_impersonate(request)
            return None

        # User is still lazy and not set up. This request may not care about
        # the current user at all. Avoid instantiating the real request.user
        # to improve performance on some requests
        get_user = request.user.__dict__['_setupfunc']

        def wrap_user():
            request.user = get_user()
            apply_impersonate(request)
            return request.user

        request.user.__dict__['_setupfunc'] = wrap_user
        request.impersonator = SimpleLazyObject(lambda: impersonator(request))
        return None
