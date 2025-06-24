# Django imports
from django.shortcuts import get_object_or_404

# DRF imports
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# drf_yasg (Swagger) imports
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Django auth models
from django.contrib.auth.models import User, Group, Permission

# Local app imports
from .models import SubAdmin
from .serializer import SubAdminSerializer
from sub_admins.permissions import IsAdmin

# Create your views here.

#--------------------Create a new subadmin---------------
@swagger_auto_schema(
    method="post",
    request_body=SubAdminSerializer,
    responses={
        201 : openapi.Response('sub-admin created successfully'),
        403 : openapi.Response('permission denied'),
        400 : openapi.Response('bad request')
    },
    operation_description="Sub-Administration Creation API",
    tags=["📦 Admin Tools"]
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_sub_admin(request , *args , **kwargs):
    """
    Create a new SubAdmin user.

    Only users with superuser status or who belong to the 'admin' group can access this endpoint.
    The request should include user details (username, email, password, etc.) and optional permission codenames.

    Returns:
        - 201 Created: SubAdmin successfully created
        - 403 Forbidden: Requesting user is not authorized
        - 400 Bad Request: Invalid or incomplete data
    """
    user = request.user
    if not user.is_superuser and not user.groups.filter(name='admin').exists():
        return Response({'message' : 'You do not have permission to create a new subadmin'} , status=403)

    serializer = SubAdminSerializer(data=request.data)
    if not serializer.is_valid():\
        return Response(serializer.errors, status=400)
    serializer.save()
    return Response({'message' : 'sub-admin created successfully'}, status=201)

#-------------------------------------------------------------



#---------------------------Update SubAdmin------------------------
@swagger_auto_schema(
    method="patch",
    request_body=SubAdminSerializer,
    responses={
        201 : openapi.Response('sub-admin created successfully'),
        400: openapi.Response('Data not in proper format'),
        403 : openapi.Response('permission denied'),
        404: openapi.Response('SubAdmin not in database'),
        500: openapi.Response('Internal server error'),

    },
    operation_description="Sub-Administration updation API",
    tags=["📦 Admin Tools"]
)
@api_view(['PATCH'])
@permission_classes([IsAdmin])
def update_sub_admin(request, sub_admin_id, *args, **kwargs):
    """
    Update an existing SubAdmin user.

    Only superusers or users in the 'admin' group are authorized to access this endpoint.
    Supports partial updates (PATCH). Validates updated data and handles permission updates securely.

    Args:
        id (int): ID of the SubAdmin to update.

    Returns:
        - 200 OK: Successfully updated
        - 400 Bad Request: Validation errors
        - 403 Forbidden: Not authorized
        - 404 Not Found: SubAdmin with given ID doesn't exist
        - 500 Internal Server Error: Unexpected issues during update
    """
    sub_admin = get_object_or_404(SubAdmin, id=sub_admin_id)
    serializer = SubAdminSerializer(sub_admin, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    try:
        serializer.save()
        return Response(
            {'message': 'Sub-admin updated successfully'},
            status=status.HTTP_200_OK
            )
    except Exception as e:
        return Response(
            {'error': f'An error occurred while updating the sub-admin: {str(e)}'},
            status=500
        )
#-------------------------------------------------------------

#-----------------------View all SubAdmins----------------------
@swagger_auto_schema(
    method="get",
    responses={
        201 : openapi.Response('sub-admin displayed successfully'),
        403: openapi.Response('permission denied'),
        404 : openapi.Response('sub-admin group not found'),
    },
    operation_description="Display all Sub-Administration API",
    tags=["📦 Admin Tools"]
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def view_all_sub_admin(request , *args , **kwargs):
    """
    Retrieve all SubAdmin users.

    This endpoint returns a list of all users associated with the 'sub-admin' group,
    excluding superusers. Only authenticated users with admin privileges (either superusers
    or members of the 'admin' group) are authorized to access this endpoint.

    Returns:
        - 200 OK: A list of serialized SubAdmin objects.
        - 403 Forbidden: If the user is not authorized to access this endpoint.
        - 404 Not Found: If the 'sub-admin' group does not exist.
    """

    try:
        sub_admins_group = Group.objects.get(name='sub-admin')
    except Group.DoesNotExist:
        return Response({'message' : "the 'sub-admin' group does not exist"}, status=404)
    users = sub_admins_group.user_set.filter(is_superuser=False)
    sub_admins = SubAdmin.objects.filter(user__in=users)

    serializer = SubAdminSerializer(sub_admins, many=True)
    return Response(serializer.data , status=201)
#-------------------------------------------------------------


#------------------------Display single subadmin---------------
@swagger_auto_schema(
    method="get",
    responses={
        201 : openapi.Response('sub-admin details displayed successfully'),
        403: openapi.Response('permission denied'),
        404 : openapi.Response('sub-admin group not found'),
    },
    operation_description="Display particular Sub-Administration API",
    tags=["📦 Admin Tools"]
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def sub_admin_details(request , sub_admin_id , *args , **kwargs):
    """
    Retrieve a single SubAdmin's details.

    This endpoint fetches a SubAdmin's full information, including associated user data,
    based on their unique ID. Only superusers or users in the 'admin' group can access it.

    Args:
        sub_admin_id (int): The ID of the SubAdmin to retrieve.

    Returns:
        - 200 OK: SubAdmin data retrieved.
        - 403 Forbidden: If the user lacks admin privileges.
        - 404 Not Found: If the SubAdmin or 'sub-admin' group does not exist.
    """
    try:
        sub_admins_group = Group.objects.get(name='sub-admin')
    except Group.DoesNotExist:
        return Response({'message' : "the 'sub-admin' group does not exist"}, status=404)
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
        200: openapi.Response(description='Sub-admin deleted successfully'),
        403: openapi.Response(description='Permission denied'),
        404: openapi.Response(description='Sub-admin or group not found'),
    },
    operation_description="API to delete a sub-admin",
    tags=["📦 Admin Tools"]
)
@api_view(['DELETE'])
@permission_classes([IsAdmin])
def delete_sub_admin(request , sub_admin_id , *args , **kwargs):
    """
    Delete a SubAdmin by ID.

    This endpoint deletes a SubAdmin user by their unique ID,
    including their associated `User` object. Only admins (superusers or members of 'admin' group) can perform this action.

    Args:
        sub_admin_id (int): The ID of the SubAdmin to delete.

    Returns:
        - 200 OK: SubAdmin deleted successfully.
        - 403 Forbidden: If the requesting user lacks admin permissions.
        - 404 Not Found: If the SubAdmin or 'sub-admin' group doesn't exist.
    """
    try:
        sub_admins_group = Group.objects.get(name='sub-admin')
    except Group.DoesNotExist:
        return Response({'message' : "the 'sub-admin' group does not exist"}, status=404)

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