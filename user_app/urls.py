from django.contrib import admin
from django.urls import path , include
from .views import user_home_page , update_user_profile , update_user_password , user_details
urlpatterns = [
    path('home/<int:id>', user_home_page, name='user_home_page'),
    path('update/<int:id>' , update_user_profile, name='update_user_profile'),
    path('update_password/<int:id>' , update_user_password, name='update_user_password'),
    path('details/<int:id>' , user_details, name='user_details'),
]