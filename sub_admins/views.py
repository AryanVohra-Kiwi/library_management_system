from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from books.models import BookStructure
from .Sub_adminForms import *
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User , Group , Permission
from user_auth.decorator import *
# Create your views here.

@login_required(login_url='login_user')
@allowed_users(allowed_users=['admin'])
def create_sub_admin(request , *args , **kwargs):
    '''
    this function is responsible for creating a new sub admin , only admins or superusers can create a new sub admin
    '''
    if request.method == 'POST':
        SubAdminForm = CreateSubAdminForm(request.POST)
        selected_permission = request.POST.getlist('subadmin_perms')
        if SubAdminForm.is_valid():
            if not selected_permission:
                messages.error(request , 'Please select a subadmin permission')
                return render(request , 'create_sub_admin.html',{'SubAdminForm' : SubAdminForm,})
            new_sub_admin_user = SubAdminForm.save()
            # handing permissions for sub-admins
            content_type = ContentType.objects.get_for_model(BookStructure) #fer content tyoe
            assigned_permission = Permission.objects.filter(codename__in=selected_permission, content_type=content_type) #checks and assignes the subadmin permissions
            new_sub_admin_user.user_permissions.set(assigned_permission)
            messages.success(request , 'SubAdmin Created Successfully , with selected permissions')
            return redirect('home_page')
        else:
            messages.error(request , 'SubAdmin Not Created')

    else:
        SubAdminForm = CreateSubAdminForm()

    context = {
        'SubAdminForm' : SubAdminForm,
    }
    return render(request , 'subadmin_pages/create_sub_admin.html' , context)

@login_required(login_url='login_user')
def update_sub_admin(request, id, *args, **kwargs):
    '''
    this function is responsible for updating an existing sub admin
    '''
    sub_admin = get_object_or_404(User , id=id)
    if request.method == 'POST':
        updated_subadmin_form = UpdateSubAdminForm(request.POST, instance=sub_admin)
        selected_permission = request.POST.getlist('subadmin_perms')

        if updated_subadmin_form.is_valid():
            updated_sub_admin_user = updated_subadmin_form.save()

        if selected_permission:
            try:
                content_type = ContentType.objects.get_for_model(BookStructure)
                valid_perm = Permission.objects.filter(
                    codename__in = selected_permission,
                    content_type=content_type,
                )
                updated_sub_admin_user.user_permissions.set(valid_perm)
            except Exception as e:
                messages.error(request , f'error updating sub admin: {e}')
            messages.success(request , 'SubAdmin Updated Successfully , with selected permissions')
            return redirect('home_page')
        else:
            messages.error(request , 'SubAdmin Not Updated')
    else:
        updated_subadmin_form = UpdateSubAdminForm(instance=sub_admin)

    #get permission
    sub_admin_perms = list(sub_admin.user_permissions.values_list('codename', flat=True))

    context = {
        'sub_admin': sub_admin,
        'updated_subadmin': updated_subadmin_form,
        'sub_admin_perms': sub_admin_perms,
    }

    return render(request, 'subadmin_pages/update_sub_admin.html', context)

@login_required(login_url='login_user')
def view_all_sub_admin(request , *args , **kwargs):
    '''
    this function is responsible for viewing all existing sub admins
    '''
    sub_admins_group = Group.objects.get(name='sub-admin')
    sub_admins = sub_admins_group.user_set.filter(is_superuser=False)
    context = {
        'subadmin_pages' : sub_admins,
    }
    return render(request , 'subadmin_pages/view_all_subadmins.html' , context)

def sub_admin_details(request , id , *args , **kwargs):
    '''
    this function is responsible for viewing an existing sub admin
    '''
    sub_admins_group = Group.objects.get(name='sub-admin')
    sub_admin = get_object_or_404(sub_admins_group.user_set.filter(is_superuser=False) , id = id)

    context = {
        'sub_admin' : sub_admin,
    }
    return render(request , 'subadmin_pages/sub_admin_details.html' , context)