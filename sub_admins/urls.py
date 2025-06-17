from django.contrib import admin
from django.urls import path , include
from .views import create_sub_admin , view_all_sub_admin , update_sub_admin , sub_admin_details , delete_sub_admin

urlpatterns = [
    path('api/create' , create_sub_admin , name='create_sub_admin'),
    path('api/view' , view_all_sub_admin , name='view_sub_admin'),
    path('api/update/<int:id>' , update_sub_admin , name='update_sub_admin'),
    path('api/details/<int:sub_admin_id>' , sub_admin_details , name='sub_admin_details'),
    path('api/delete/<int:sub_admin_id>' , delete_sub_admin , name='delete_sub_admin'),
]