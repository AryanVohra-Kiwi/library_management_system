from pyexpat.errors import messages
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render, get_object_or_404
from user_auth.decorator import *
from django.contrib.auth.decorators import login_required
from .models import CustomerCreate
from .serializer import CustomerSerializer , CustomerUpdateSerializer , PasswordChnageSerializer
from django.contrib.auth.forms import PasswordChangeForm
from books.models import *

from rest_framework import status
from rest_framework.decorators import api_view , permission_classes , parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.

#------------Get user details------------------------------
@swagger_auto_schema(
    method="get",
    responses={
        200 : openapi.Response('success'),
        403 : openapi.Response('not the correct user')
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_details(request , user_id , *args, **kwargs):
    customer = get_object_or_404(CustomerCreate, user=user_id)
    if request.user != customer.user:
        return Response({'message':'You are not the correct user'} , status=403)
    serializer = CustomerSerializer(customer).data
    return Response(
        {'messages' : 'success',
            'data': serializer
         }, status = 200,
    )
#----------------------------------------------------------


#------------------Update User Profile---------------

@swagger_auto_schema(
    method="patch",
    request_body=CustomerUpdateSerializer,
    responses={
        200 : openapi.Response('success'),
        403 : openapi.Response('not the correct user'),
        400 : openapi.Response('Error updating user')
    }
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser , FormParser])
def update_user_profile(request , id , *args , **kwargs):
    # Prevent Swagger schema generation from breaking
    if getattr(request, 'swagger_fake_view', False):
        return Response(status=200)
    user_detail = get_object_or_404(CustomerCreate, user=id)
    #check if the user updating the value is the same as the one accessing.
    if request.user != user_detail.user:
        return Response({'message': 'You are not the correct user'}, status=403)
    update_serializer = CustomerUpdateSerializer(user_detail , data=request.data , partial=True)
    if update_serializer.is_valid():
        update_serializer.save()
        return Response(
            {'messages' : 'successfully updated user',}
        )
    return Response(update_serializer.errors, status=400)
#------------------------------------------------------


#---------------------------------Update a user password-----------------
@swagger_auto_schema(
    method="patch",
    request_body=PasswordChnageSerializer,
    responses={
        200 : openapi.Response('successfully updated password'),
        403 : openapi.Response('not the correct user'),
        400 : openapi.Response('Error updating user')
    }
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_password(request, id , *args , **kwargs):
    user_detail = get_object_or_404(CustomerCreate, user=id)
    if request.user != user_detail.user:
        return Response({'message': 'You are not the correct user'}, status=403)
    password_serializer = PasswordChnageSerializer(user_detail)
    if password_serializer.is_valid():
        password_serializer.save()
        return Response({'messages' : 'successfully updated password'})
    return Response(password_serializer.errors, status=400)
#-------------------------------------------------------------------------



#--------------Do after we make the issue api---------------------------------
def user_orders(request , id  , *args , **kwargs):
    customer = CustomerCreate.objects.get(user=request.user)
    issued_book = IssueBook.objects.filter(issued_by=customer).all()
    try:
        book_copy_id = issued_book.first().book.book_instance.id
    except AttributeError:
        book_copy_id = None
    context = {
        'issued_book': issued_book,
        'customer': customer,
        'book_copy_id' :book_copy_id,
    }
    return render(request,  'user_pages/user_orders.html', context)
#-----------------------------------------------------------------