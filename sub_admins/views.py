from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import status
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import SubAdmin
from .serializer import SubAdminSerializer
from books.models import BookStructure
from .Sub_adminForms import *
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User , Group , Permission
from user_auth.decorator import *
# Create your views here.

#--------------------Create a new subadmin---------------
@swagger_auto_schema(
    method="post",
    request_body=SubAdminSerializer,
    responses={
        201 : openapi.Response('sub-admin created successfully'),
        403 : openapi.Response('permission denied'),
        400 : 'bad request'
    },
    operation_description="Sub-Administration Creation API"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_sub_admin(request , *args , **kwargs):
    '''
    this function is responsible for creating a new sub admin , only admins or superusers can create a new sub admin
    '''
    user = request.user
    if not user.is_superuser and not user.objects.filter(name='admin').exists():
        return Response({'message' : 'You do not have permission to create a new subadmin'} , status=403)

    serializer = SubAdminSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message' : 'sub-admin created successfully'}, status=201)
    return Response(serializer.errors, status=400)
#-------------------------------------------------------------



#---------------------------Update SubAdmin------------------------
@swagger_auto_schema(
    method="patch",
    request_body=SubAdminSerializer,
    responses={
        201 : openapi.Response('sub-admin created successfully'),
        403 : openapi.Response('permission denied'),
    },
    operation_description="Sub-Administration updation API"
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_sub_admin(request, id, *args, **kwargs):
    '''
    this function is responsible for updating an existing sub admin
    '''
    sub_admin = get_object_or_404(User , id=id)
    serializer = SubAdminSerializer(sub_admin , data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message' : 'sub-admin updated successfully'}, status=201)
    return Response(serializer.errors, status=400)
#-------------------------------------------------------------

#-----------------------View all SubAdmins----------------------
@swagger_auto_schema(
    method="get",
    responses={
        201 : openapi.Response('sub-admin created successfully'),
        400 : openapi.Response('sub-admin does not exist'),
    },
    operation_description="Display all Sub-Administration API"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_sub_admin(request , *args , **kwargs):
    '''
    this function is responsible for viewing all existing sub admins
    '''
    sub_admins_group = Group.objects.get(name='sub-admin')
    users = sub_admins_group.user_set.filter(is_superuser=False)
    sub_admins = SubAdmin.objects.filter(user__in=users)
    if not sub_admins.exists():
        return Response({'message' : 'sub-admin does not exist'}, status=400)
    serializer = SubAdminSerializer(sub_admins, many=True)
    return Response(serializer.data , status=201)
#-------------------------------------------------------------


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