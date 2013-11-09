from .helpers import check_allow_for_user, check_allow_for_uri

try:
    # Django 1.5 check
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()

class ImpersonateMiddleware(object):
    def process_request(self, request):
        request.user.is_impersonate = False
        request.impersonator = None

        if request.user.is_authenticated() and \
           '_impersonate' in request.session:
            new_user_id = request.session['_impersonate']
            try:
                new_user = User.objects.get(id=new_user_id)
            except User.DoesNotExist:
                return

            if check_allow_for_user(request, new_user) and \
               check_allow_for_uri(request.path):
                request.impersonator = request.user
                request.user = new_user
                request.user.is_impersonate = True
