from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def student_required(view_func):
    """Decorator to restrict view to students only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('student_login')
        if not request.user.is_student:
            messages.error(request, 'This page is only for students.')
            return redirect('admin_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator to restrict view to admins only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if request.user.is_student:
            messages.error(request, 'This page is only for admins.')
            return redirect('student_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def voting_page_required(view_func):
    """Decorator to restrict voting pages to students only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('student_login')
        if not request.user.is_student:
            messages.error(request, 'This page is only for students.')
            return redirect('admin_dashboard')
        if not request.user.password_changed:
            messages.warning(request, 'Please change your password first.')
            return redirect('change_password_first')
        return view_func(request, *args, **kwargs)
    return wrapper
