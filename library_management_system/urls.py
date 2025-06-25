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
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from user_auth.views import (
    register_user,
    login_user,
    logout_user,
    get_new_access_token,
    verify_email
)

# Swagger schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Library API Documentation",
        default_version='v1',
        description="Comprehensive documentation for the Django REST API.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    # 🔐 Authentication Routes
    path('api/register/', register_user, name='register_user'),
    path('api/login/', login_user, name='login_user'),
    path('api/logout/', logout_user, name='logout_user'),
    path('api/new-access-token/', get_new_access_token, name='new_access_token'),
    path('api/verify_email/', verify_email, name='verify_email'),

    # ⚙️ Admin Route
    path('admin/', admin.site.urls),

    # 📚 App-Specific Routes
    path('books/', include('books.urls'), name='books'),
    path('sub-admin/', include('sub_admins.urls'), name='sub_admins'),
    path('user-profile/', include('user_app.urls'), name='user_profile'),

    # 📄 Swagger Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

# 🖼️ Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
