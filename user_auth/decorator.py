from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render , redirect
from django.contrib.auth.models import Permission

#described the decorators here
def unauthenticated_user(view_func):
    def wrapper_func(request , *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home_page')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def admin_only(allowed_users=[]):
    def decorator(view_func):
        def wrapper_func(request , *args , **kwargs):
            user = request.user
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            if user.groups.filter(name__in=allowed_users).exists():
                return view_func(request, *args, **kwargs)
            else:
                return redirect('user_home_page' , id=request.user.id)
        return wrapper_func
    return decorator


def allowed_users(allowed_users=[] , allowed_permissions=[]):
    def decorator(view_func):
        def wrapper_func(request , *args, **kwargs):
            user = request.user
            user_groups = user.groups.values_list('name', flat=True)
            if any(group in allowed_users for group in user_groups):
                if allowed_permissions:
                    user_permissions = user.get_all_permissions()
                    for perms in allowed_permissions:
                        if perms not in user_permissions:
                            return HttpResponse('Permission Denied : Missing Permission')
                return view_func(request, *args, **kwargs)
            return HttpResponse('Unauthorized : do not have the required role')
        return wrapper_func
    return decorator



