from django.shortcuts import get_object_or_404, redirect, render

from . import contexts, logic
from .decorators import allowed_user_required
from .helpers import User, get_redir_path


@allowed_user_required
def impersonate(request, uid):
    ''' Takes in the UID of the user to impersonate.
        View will fetch the User instance and store it
        in the request.session under the '_impersonate' key.

        The middleware will then pick up on it and adjust the
        request object as needed.

        Also store the user's 'starting'/'original' URL so
        we can return them to it.
    '''
    uid = str(uid).strip()
    if uid.isdigit():
        new_user = get_object_or_404(User, pk=uid)
    elif '@' in uid:
        new_user = get_object_or_404(User, email=uid)
    else:
        new_user = get_object_or_404(User, username=uid)
    logic.stop_impersonate(request)
    logic.impersonate(request, new_user)
    return redirect(get_redir_path(request))


def stop_impersonate(request):
    ''' Remove the impersonation object from the session
        and ideally return the user to the original path
        they were on.
    '''
    dest = logic.stop_impersonate(request)
    return redirect(dest)


@allowed_user_required
def list_users(request):
    list_context = contexts.get_list_template_context(request)
    return render(request, 'impersonate/list_users.html', list_context)


@allowed_user_required
def search_users(request):
    ''' Simple search through the users.
        Will add 7 items to the context.
          * users - All users that match the query passed.
          * paginator - Django Paginator instance
          * page - Current page of objects (from Paginator)
          * page_number - Current page number, defaults to 1
          * query - The search query that was entered
          * redirect - arg for redirect target, e.g. "?next=/foo/bar"
          * redirect_field - hidden input field with redirect argument,
                              put this inside search form
    '''
    search_query = request.GET.get('q', '')
    search_context = contexts.get_search_template_context(
        request, search_query)

    return render(request, 'impersonate/search_users.html', search_context)
