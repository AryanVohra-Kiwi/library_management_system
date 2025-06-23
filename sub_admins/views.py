from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import SubAdmin
from .serializer import SubAdminSerializer
from django.contrib.auth.models import User , Group , Permission
from sub_admins.permissions import IsAdmin
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
@permission_classes([IsAdmin])
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
@permission_classes([IsAdmin])
def update_sub_admin(request, id, *args, **kwargs):
    '''
    This function is responsible for updating an existing sub admin
    '''
    try:
        sub_admin = get_object_or_404(SubAdmin, id=id)
        serializer = SubAdminSerializer(sub_admin, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Sub-admin updated successfully'},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {'error': f'An error occurred while updating the sub-admin: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
#-------------------------------------------------------------

#-----------------------View all SubAdmins----------------------
@swagger_auto_schema(
    method="get",
    responses={
        201 : openapi.Response('sub-admin displayed successfully'),
        400 : openapi.Response('sub-admin does not exist'),
    },
    operation_description="Display all Sub-Administration API"
)
@api_view(['GET'])
@permission_classes([IsAdmin])
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


#------------------------Display single subadmin---------------
@swagger_auto_schema(
    method="get",
    responses={
        201 : openapi.Response('sub-admin displayed successfully'),
        400 : openapi.Response('sub-admin does not exist'),
    },
    operation_description="Display particular Sub-Administration API"
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def sub_admin_details(request , sub_admin_id , *args , **kwargs):
    '''
    this function is responsible for viewing an existing sub admin
    '''
    sub_admins_group = Group.objects.get(name='sub-admin')
    try:
        sub_admins = SubAdmin.objects.select_related('user').get(
            id=sub_admin_id,
            user__groups=sub_admins_group,
            user__is_superuser=False
        )
    except SubAdmin.DoesNotExist:
        return Response({'message' : 'sub-admin does not exist'}, status=400)
    serializer = SubAdminSerializer(sub_admins)
    return Response(serializer.data , status=200)
#--------------------------------------------------------------

#--------------Delete SubAdmin----------------
@swagger_auto_schema(
    method="delete",
    responses={
        201 : openapi.Response('sub-admin displayed successfully'),
        400 : openapi.Response('sub-admin does not exist'),
    },
    operation_description="Display particular Sub-Administration API"
)
@api_view(['DELETE'])
@permission_classes([IsAdmin])
def delete_sub_admin(request , sub_admin_id , *args , **kwargs):
    '''
    this function is responsible for viewing an existing sub admin
    '''
    sub_admins_group = Group.objects.get(name='sub-admin')
    try:
        sub_admins = SubAdmin.objects.select_related('user').get(
            id=sub_admin_id,
            user__groups=sub_admins_group,
            user__is_superuser=False
        )
    except SubAdmin.DoesNotExist:
        return Response({'message' : 'sub-admin does not exist'}, status=400)
    sub_admins.user.delete()
    return Response({'message' : 'sub-admin deleted successfully'}, status=201)
#------------------------------------------------