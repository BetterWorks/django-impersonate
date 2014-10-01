from .helpers import check_allow_for_user, check_allow_for_uri, User


class ImpersonateMiddleware(object):
    def process_request(self, request):
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
