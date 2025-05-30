from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from books.models import BookStructure
from user_app.user_form import UserForm
from .auth_froms import CreateNormalUserForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User , Group , Permission
from .decorator import *
# Create your views here.

@unauthenticated_user
def register_user(request ,*args , **kwargs):
    '''
    this function takes in a registration model form and uses that to register new users
    note: two users can not have the same username
    '''
    if request.method == 'POST':
        user_registration_form = CreateNormalUserForm(request.POST)
        if user_registration_form.is_valid():
            existing_user = User.objects.filter(
                username=user_registration_form.cleaned_data['username']
            ).exists()
            if not existing_user:
                new_user = user_registration_form.save()

                messages.success(request , 'Account Created Successfully')
                return redirect('login_user') #reditects to login
            else:
                messages.error(request , 'Username Already Taken')
        else:
            print(user_registration_form.errors)
            messages.error(request , 'Account Not Created')
    else:
        user_registration_form = CreateNormalUserForm()

    context = {
        'registration_form' : user_registration_form,
    }
    return render(request , 'register.html' , context)

@unauthenticated_user
def login_user (request , *args , **kwargs):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        authenticated_user = authenticate(request , username=username , password=password)
        if authenticated_user is not None:
            login(request , authenticated_user)
            messages.success(request , 'login successful')
            return redirect('home_page') #redirects to the main home page
        else:
            messages.error(request , 'username or password is not valid')

    context = {}
    return render(request , 'login.html' , context)

@login_required(login_url='login_user')
@admin_only(allowed_users=['admin' , 'sub-admin'])
def main_page(request , *args , **kwargs):
    user = request.user
    user_group = user.groups.values_list('name' , flat=True)
    print(user_group)
    context = {
        'user_group' : user_group,
    }
    return render(request , 'home.html' ,context)

@login_required(login_url='login_user')
def logout_user(request , *args, **kwargs):
    logout(request)
    return redirect('login_user')


