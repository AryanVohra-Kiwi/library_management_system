from tokenize import TokenError

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from books import serializer
from .serializer import RegisterSerializer, LoginSerializer, LogoutSerializer, GenerateAccessTokenSeralizer
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.
#--------------------------------Reguster User-------------------------
@swagger_auto_schema(
    method="post",
    request_body=RegisterSerializer,
    responses={
        201 : openapi.Response('User Registered Successfully'),
        400 : openapi.Response('error occured making a new user'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request ,*args , **kwargs):
    '''
    this function takes in a registration model form and uses that to register new users
    note: two users can not have the same username
    '''
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message' : 'User Registered Successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#-------------------------------------------------------------------------

#-----------------------------Generate New Access Token------------------------
@swagger_auto_schema(
    method="post",
    request_body=GenerateAccessTokenSeralizer,
    responses={
        200 : openapi.Response('generated successfully'),
        400 : openapi.Response('error occured making a token'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def get_new_access_token(request):
    serializer = GenerateAccessTokenSeralizer(data=request.data)
    if serializer.is_valid():
        try:
            refresh_token = RefreshToken(serializer.token)
            new_access_token = str(refresh_token.access_token)
            return Response(
                {
                    'access_token' : new_access_token,
                    'token_type': 'Bearer',
                    'auth_header': f'Bearer {new_access_token}'
                 }
            )
        except TokenError:
            return Response({'message' : 'token expired'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#--------------------------------------------------------------------------------

#-----------------------------Log the user in and return jwt token------------------
@swagger_auto_schema(
    method="post",
    request_body=LoginSerializer,
    responses={
        201 : openapi.Response('User Logged Successfully'),
        400 : openapi.Response('error while login in'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user (request , *args , **kwargs):
    '''
    This function is responsible for logging the user
    '''
    login_serializer = LoginSerializer(data=request.data)
    if login_serializer.is_valid():
        username = login_serializer.validated_data['username']
        password = login_serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'message' : 'User not Authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)

        return Response({
            'message' : 'User Logged In',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
    operation_description="Logout User API"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request , *args, **kwargs):
    serializer = LogoutSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message' : 'User Logged Out'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#----------------------------------------------------------------

