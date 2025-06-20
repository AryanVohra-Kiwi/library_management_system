from django.contrib import admin
from django.urls import path , include
from .views import update_user_profile , update_user_password , user_details , user_orders
urlpatterns = [
    path('api/update/<int:id>' , update_user_profile, name='update_user_profile'),
    path('api/update_password/<int:id>' , update_user_password, name='update_user_password'),
    path('api/details/<int:user_id>' , user_details, name='user_details'),
    path('orders/<int:id>', user_orders , name='user_orders' ),
]