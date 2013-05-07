from .helpers import check_allow_for_user, check_allow_for_uri


class ImpersonateMiddleware(object):
    def process_request(self, request):
        request.user.is_impersonate = False

        if request.user.is_authenticated() and \
           '_impersonate' in request.session:
            new_user = request.session['_impersonate']
            new_user.real_user = request.user

            if check_allow_for_user(request, new_user) and \
               check_allow_for_uri(request.path):
                request.user = new_user
                request.user.is_impersonate = True
