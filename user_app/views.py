from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from user_auth.decorator import *
from django.contrib.auth.decorators import login_required
from .models import CustomerCreate
from .user_form import UpdateCustomer
from django.contrib.auth.forms import PasswordChangeForm
from books.models import *
# Create your views here.
@login_required(login_url='login_user')
def user_home_page(request, id, *args, **kwargs):
    customer = get_object_or_404(CustomerCreate, user=id)
    context = {
        'customer': customer,
    }
    return render(request, 'user_pages/user_home_page.html', context)

def user_details(request , id , *args, **kwargs):
    customer = get_object_or_404(CustomerCreate, user=id)
    if request.user != customer.user:
        return redirect('user_details', id=request.user.id)
    context = {
         'customer': customer,
     }
    return render(request, 'user_pages/user_details.html', context)

@login_required(login_url='login_user')
def update_user_profile(request , id , *args , **kwargs):
    user_detail = get_object_or_404(CustomerCreate, user=id)
    updated_user = UpdateCustomer(request.POST, files=request.FILES ,instance=user_detail)
    if request.user != user_detail.user:
        return redirect('update_user_profile', id=request.user.id)
    if request.method == 'POST':
        if updated_user.is_valid():
            updated_user.save()
            return redirect('user_details', id=request.user.id)
    else:
        updated_user = UpdateCustomer(instance=user_detail)
    context = {
        'user': user_detail,
        'update_user': updated_user,
    }
    return render(request, 'user_pages/update_user_profile.html' ,context)

@login_required(login_url='login_user')
def update_user_password(request, id , *args , **kwargs):
    user_detail = get_object_or_404(CustomerCreate, user=id)
    if request.user != user_detail.user:
        return redirect('update_user_password   ', id=request.user.id)
    if request.method == 'POST':
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            password_form.save()
            return redirect('login_user')
    else:
        password_form = PasswordChangeForm(user=request.user)
    context = {
        'user': user_detail,
        'pass_form': password_form,
    }
    return render(request, 'user_pages/update_user_password.html' ,context)

def user_orders(request , id  , *args , **kwargs):
    customer = CustomerCreate.objects.get(user=request.user)
    issued_book = IssueBook.objects.filter(issued_by=customer).all()
    book_copy_id = issued_book.first().book.book_instance.id
    context = {
        'issued_book': issued_book,
        'customer': customer,
        'book_copy_id' :book_copy_id,
    }
    return render(request, 'user_pages/user_orders.html', context)