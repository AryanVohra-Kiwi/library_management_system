from pyexpat.errors import messages
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render, get_object_or_404
from .serializer import CustomerSerializer, CustomerUpdateSerializer, PasswordChnageSerializer, IssueBookSerializer
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
        200 : openapi.Response('Successfully Retrived user details'),
        403 : openapi.Response('Unauthorized , You are not authorized user.'),
        404 : openapi.Response('user not found')
    },
    operation_description="API to Retrieves user details",
    tags=["👤 User Operations"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_details(request , user_id , *args, **kwargs):
    """
    Retrieve a user's customer profile.
    Only the owner of the profile can access this information.
    """
    customer = get_object_or_404(CustomerCreate, user_id=user_id)
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
        200 : openapi.Response('Successfully Updated user details'),
        403 : openapi.Response('Unauthorized , You are not authorized user'),
        400 : openapi.Response('Bad Request - Validation Error')
    },
    operation_description="API to Update user details",
    tags=["👤 User Operations"]
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser , FormParser])
def update_user_profile(request , id , *args , **kwargs):
    """
   PATCH : api/update/<int:id>

    Allows an authenticated user to update their own profile.
    Fields like first_name, last_name, age, phone, profile_picture can be updated.

    Restrictions:
    - Only the logged-in user can update their own profile.
    """

    # Prevent Swagger schema generation from breaking
    if getattr(request, 'swagger_fake_view', False):
        return Response(status=200)


    customer = get_object_or_404(CustomerCreate, user=id)
    #check if the user updating the value is the same as the one accessing.
    if request.user != customer.user:
        return Response({'message': 'You are not the correct user'}, status=403)

    update_serializer = CustomerUpdateSerializer(customer , data=request.data , partial=True)
    if not update_serializer.is_valid():
        return Response(update_serializer.errors, status=400)
    update_serializer.save()

    return Response(
        {'messages' : 'successfully updated user',},
        status=200,
    )

#------------------------------------------------------


#---------------------------------Update a user password-----------------
@swagger_auto_schema(
    method="patch",
    request_body=PasswordChnageSerializer,
    responses={
        200: openapi.Response('Password updated successfully'),
        403: openapi.Response('You are not authorized'),
        400: openapi.Response('Invalid input or old password mismatch')
    },
    operation_description="API to Update user password",
    tags=["👤 User Operations"]
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_password(request, id , *args , **kwargs):
    """
    PATCH : api/update_password/<int:id>

    Allows an authenticated user to change their password.
    Requires old_password, new_password, and confirm_password fields.
    """
    customer = get_object_or_404(CustomerCreate, user=id)
    if request.user != customer.user:
        return Response({'message': 'You are not the correct user'}, status=403)

    password_serializer = PasswordChnageSerializer(data=request.data)
    if not password_serializer.is_valid():
        return Response(password_serializer.errors, status=400)
    old_password = password_serializer.validated_data['old_password']
    new_password= password_serializer.validated_data['new_password']
    user = customer.user

    if not user.check_password(old_password):
        return Response({'message': 'old password entered is incorrect'}, status=400)
    user.set_password(new_password)
    user.save()
    return Response({'messages' : 'successfully updated password'})

#-------------------------------------------------------------------------



#--------------Do after we make the issue api---------------------------------
@swagger_auto_schema(
    method="get",
    responses={
        200 : openapi.Response('Successfullt retrieved user issued books'),
        403 : openapi.Response('User not authenticated or unauthorized '),
    },
    operation_description="API to retrieve user issued books",
    tags=["👤 User Operations"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders(request  , *args , **kwargs):
    """
    Retrieve books issued to the currently authenticated user.

    This endpoint fetches all book issues (IssueBook records) associated with the logged-in user.
    It also optionally returns the `book_copy_id` of the first issued book, if available.

    Permissions:
    - Only authenticated users can access this endpoint.

    Returns:
    - 200 OK: A list of all issued books and the first book copy ID (if any).
    - 403 Forbidden: If the request is made by an unauthenticated user.
    """

    customer = get_object_or_404(CustomerCreate, user=request.user)
    issued_book = IssueBook.objects.filter(issued_by=customer).all()
    try:
        book_copy_id = issued_book.first().book.book_instance.id
    except AttributeError:
        book_copy_id = None

    issue_book_seralizer = IssueBookSerializer(issued_book , many=True)
    return Response(
        {
            'issued_books' : issue_book_seralizer.data,
            'book_copy_id' : book_copy_id
        }
    )
#-----------------------------------------------------------------