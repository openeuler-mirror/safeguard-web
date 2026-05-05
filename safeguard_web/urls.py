from django.contrib import admin
from django.urls import path,include
from rest_framework import routers, permissions
from backend import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from backend.views import UsersViewSet

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet, basename="users")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls',namespace='rest_framework')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

urlpatterns += router.urls