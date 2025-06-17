from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .auth_froms import CreateNormalUserForm
from django.contrib.auth.models import User , Group , Permission
from rest_framework import status
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializer import RegisterSerializer , LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed

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
def main_page(request , *args , **kwargs):
    '''
    this is the admin page for the site , we made sure only admins and suadmins can access tis page
    '''
    user = request.user
    user_group = user.groups.values_list('name' , flat=True)
    print(user_group)
    context = {
        'user_group' : user_group,
    }
    return render(request , 'home.html' ,context)


def logout_user(request , *args, **kwargs):
    '''
    This function is responsible for logging out the user
    This function is responsible for logging out the user
    '''
    logout(request)
    return redirect('login_user')
