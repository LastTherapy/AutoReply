from django.shortcuts import redirect
from functools import wraps
from .views import get_current_hh_user


def hh_authenticated(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = get_current_hh_user(request)
        if not user:
            return redirect('hh_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
