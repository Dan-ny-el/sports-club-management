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
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            user_groups = set(request.user.groups.values_list('name', flat=True))
            if user_groups.intersection(allowed_roles):
                return view_func(request, *args, **kwargs)

            raise PermissionDenied
        return _wrapped_view
    return decorator

admin_required = role_required('Admin')
captain_or_admin_required = role_required('Admin', 'Team Captain')
student_or_above_required = role_required('Admin', 'Team Captain', 'Student')