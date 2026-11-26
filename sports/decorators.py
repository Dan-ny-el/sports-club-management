from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

def role_required(*allowed_roles):
    """
    Restrict access to a view based on user roles."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator 

admin_required = role_required('Admin')
captain_or_admin_required = role_required('Admin',  'manager')
student_or_above_required = role_required('Admin', 'manager', 'Student')