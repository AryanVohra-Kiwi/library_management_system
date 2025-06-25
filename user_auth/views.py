from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializer import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    GenerateAccessTokenSerializer, VerifyOTPSerializer,
)




# Create your views here.
#--------------------------------Reguster User-------------------------
@swagger_auto_schema(
    method="post",
    request_body=RegisterSerializer,
    responses={
        201 : openapi.Response('User Registered Successfully'),
        400 : openapi.Response('error occured making a new user'),
    },
    operation_description="API to register the user",
    tags=["🔑Authentication"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request ,*args , **kwargs):
    """
    Register a new user.

    Accepts:
    - username: Unique string identifier for the user.
    - email: User's email address.
    - password: Password for the account.
    - confirm_password: Confirmation of the password.

    Returns:
    - 201 Created: If the user is successfully registered.
    - 400 Bad Request: If validation fails or user already exists.
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user_information = {
            'username': user.username,
            'email': user.email,
        }
        return Response(
            {
                    'message' : 'User Registered Successfully',
                    'user_information' : user_information

                },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#-------------------------------------------------------------------------

#-----------------------------Generate New Access Token------------------------
@swagger_auto_schema(
    method="post",
    request_body=GenerateAccessTokenSerializer,
    responses={
        200 : openapi.Response('New Access Token Generated Successfully'),
        400 : openapi.Response('Missing Refresh Token'),
        401 : openapi.Response('Refresh Token has expired or is invalid'),
    },
    operation_description="API to generate a new access token",
    tags=["🔑Authentication"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def get_new_access_token(request):
    """
    Generate a new access token using a valid refresh token.

    Returns:
    - 200 OK with access token if the refresh token is valid.
    - 400 Bad Request if validation fails.
    - 401 Unauthorized if token is invalid or expired.
    """
    serializer = GenerateAccessTokenSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        refresh_token = serializer.refresh
        new_access_token = str(refresh_token.access_token)
        return Response(
            {
                'access_token' : new_access_token,
                'token_type': 'Bearer',
                'auth_header': f'Bearer {new_access_token}'
                } , status=status.HTTP_200_OK
        )
    except TokenError:
        return Response({'Token Error' : 'Token is invalid or has expired'}  , status=status.HTTP_401_UNAUTHORIZED)

#--------------------------------------------------------------------------------

#-----------------------------Log the user in and return jwt token------------------
@swagger_auto_schema(
    method="post",
    request_body=LoginSerializer,
    responses={
        201 : openapi.Response('User Logged Successfully'),
        400 : openapi.Response('Invalid Credentials'),
        401 : openapi.Response('Authentication Failed'),
    },
    operation_description="API for login returns JWT token",
    tags=["🔑Authentication"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user (request , *args , **kwargs):
    """
    Authenticates a user and returns JWT tokens.

    Accepts:
        - username
        - password

    Returns:
        - access: JWT access token
        - refresh: JWT refresh token
        - token_type: 'Bearer'
        - auth_header: Full Authorization header
    """
    login_serializer = LoginSerializer(data=request.data)
    if not login_serializer.is_valid():
        return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    username = login_serializer.validated_data['username']
    password = login_serializer.validated_data['password']

    user = authenticate(username=username, password=password)
    if not user:
         return Response({'message' : 'User not Authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    return Response(
            {
                'message' : 'User Logged In',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'Token Type' : 'Bearer',
                'auth header' : f'Bearer {access_token}'
            },
        status=status.HTTP_200_OK
    )

#-----------------------------------------------

#----------------------------------Logout---------------------------------
#NOTE : ONLY BLACKLIST THE REGFRESH TOKEN AND NOT THE ACCESS TOKEN
@swagger_auto_schema(
    method="post",
    request_body=LogoutSerializer,
    responses={
        201 : openapi.Response('User Logged Successfully'),
        400 : openapi.Response('error occured making a new user'),
    },
    operation_description="Logout User API",
    tags=["🔑Authentication"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request , *args, **kwargs):
    """
    Logout the authenticated user by blacklisting their refresh token.

    Requires:
    - refresh_token: The JWT refresh token to be invalidated.

    Returns:
    - 200 OK on successful logout
    - 400 Bad Request if the refresh token is missing or invalid
    """
    serializer = LogoutSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response({'message' : 'User Logged Out'}, status=status.HTTP_200_OK)

#----------------------------------------------------------------

#-----------------------------Verify OTP------------------
@swagger_auto_schema(
    method="post",
    request_body=VerifyOTPSerializer,
    responses={
        201 : openapi.Response('Email Verified'),
        400 : openapi.Response('Couldnt verify email'),
    },
    operation_description="Verify email",
    tags=["🔑Authentication"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
#----------------------------------------------------------------