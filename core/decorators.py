from django.http import HttpResponseForbidden
from functools import wraps


def role_required(allowed_roles):
    """
    Decorator to allow only users with specific role IDs or superuser to access the view.
    Usage:
        @role_required([1, 2, 3])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            id_vaitro = getattr(
                getattr(user, 'vaitro', None), 'id_vaitro', None)
            if id_vaitro in allowed_roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Bạn không có quyền truy cập vào chức năng này.")
        return _wrapped_view
    return decorator
