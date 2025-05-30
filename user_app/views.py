from django.shortcuts import render
from user_auth.decorator import *
from django.contrib.auth.decorators import login_required
from .models import CustomerCreate
# Create your views here.
@login_required(login_url='login_user')
def user_home_page(request , id , *args, **kwargs):
    customer = CustomerCreate(id=id)
    context = {
        'customer': customer,
    }
    return render(request, 'user_pages/user_home_page.html', context)
