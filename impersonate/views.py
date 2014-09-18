from .decorators import allowed_user_required
from .helpers import get_redir_path
from django.shortcuts import redirect, render, get_object_or_404
import contexts
import logic

try:
    # Django 1.5 check
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()


def impersonate(request, uid):
    new_user = get_object_or_404(User, pk=uid)
    logic.stop_impersonate(request)
    logic.impersonate(request, new_user)
    return redirect(get_redir_path(request))


def stop_impersonate(request):
    logic.stop_impersonate(request)
    return redirect(get_redir_path(request))


@allowed_user_required
def list_users(request, template):
    list_context = contexts.get_list_template_context(request)
    return render(request, template, list_context)


@allowed_user_required
def search_users(request, template):
    search_query = request.GET.get('q', '')
    search_context = contexts.get_search_template_context(
        request, search_query)

    return render(request, template, search_context)
