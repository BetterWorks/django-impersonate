from django.shortcuts import get_object_or_404, redirect, render

from . import contexts, logic
from .decorators import allowed_user_required
from .helpers import get_redir_path

try:
    # Django 1.5 check
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()


@allowed_user_required
def impersonate(request, uid):
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
