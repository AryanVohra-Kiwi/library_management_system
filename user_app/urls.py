from django.contrib import admin
from django.urls import path , include
from .views import user_home_page
urlpatterns = [
    path('<int:id>', user_home_page, name='user_home_page'),
]