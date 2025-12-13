from django.shortcuts import redirect
from functools import wraps

def solo_asistentes(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'rol', None) == 'asistente':
            return view_func(request, *args, **kwargs)
        return redirect('no_autorizado')  # Puedes crear esta vista o usar una genérica
    return _wrapped_view

def solo_organizadores(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'rol', None) == 'organizador':
            return view_func(request, *args, **kwargs)
        return redirect('no_autorizado')
    return _wrapped_view

def solo_administradores(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'rol', None) == 'administrador':
            return view_func(request, *args, **kwargs)
        return redirect('no_autorizado')
    return _wrapped_view

def solo_desarrolladores(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'rol', None) == 'desarrollador':
            return view_func(request, *args, **kwargs)
        return redirect('no_autorizado')
    return _wrapped_view

def solo_soporte(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'rol', None) == 'soporte':
            return view_func(request, *args, **kwargs)
        return redirect('no_autorizado')
    return _wrapped_view
