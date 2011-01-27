from django.conf import settings


class ImpersonateMiddleware(object):
    def process_request(self, request):
        if request.user.is_superuser and '_impersonate' in request.session:
            request.user = request.session['_impersonate']
            request.user._impersonate = True
