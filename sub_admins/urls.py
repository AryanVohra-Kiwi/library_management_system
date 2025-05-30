from django.contrib import admin
from django.urls import path , include
from .views import create_sub_admin , view_all_sub_admin , update_sub_admin , sub_admin_details

urlpatterns = [
    path('create' , create_sub_admin , name='create_sub_admin'),
    path('view' , view_all_sub_admin , name='view_sub_admin'),
    path('update/<int:id>' , update_sub_admin , name='update_sub_admin'),
    path('details/<int:id>' , sub_admin_details , name='sub_admin_details'),
]