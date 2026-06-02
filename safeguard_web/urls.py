from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth routes
    path('api/auth/', include('backend.urls.auth')),

    # User routes
    path('api/', include('backend.urls.user')),

    # Authority routes
    path('api/authority/', include('backend.urls.authority')),

    # Host routes
    path('api/', include('backend.urls.host')),

    # OSDeploy routes
    path('api/', include('backend.urls.osdeploy')),

    # Network routes
    path('api/', include('backend.urls.network')),

    # Security routes
    path('api/', include('backend.urls.security')),

    # Task routes
    path('api/', include('backend.urls.task')),

    # OSmigrate routes
    path('api/', include('backend.urls.osmigrate')),

    # DRF auth
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(
        permission_classes=[permissions.AllowAny],
        authentication_classes=[]
    ), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(
        permission_classes=[permissions.AllowAny],
        authentication_classes=[],
        url_name='schema'
    ), name='swagger-ui'),
]
