"""
URL configuration for library_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from tkinter.font import names

from django.contrib import admin
from django.urls import path , include
from user_auth.views import register_user , login_user , main_page , logout_user
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', login_user, name='login_user'),
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('home/', main_page, name='home_page'),
    path('logout/' , logout_user , name='logout_user'),
    path('admin/', admin.site.urls),
    path('books/', include('books.urls') , name='Library'),
    path('sub_admin/', include('sub_admins.urls')),
    path('user_profile/', include('user_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
