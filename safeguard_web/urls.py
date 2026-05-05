from django.contrib import admin
from django.urls import path,include
from rest_framework import routers, permissions
from backend import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from backend.views import UsersViewSet, LoginView

router = routers.DefaultRouter()
router.register(r'api/users', UsersViewSet, basename="users")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls',namespace='rest_framework')),

    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[permissions.AllowAny],  authentication_classes=[]), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(permission_classes=[permissions.AllowAny],  authentication_classes=[], url_name='schema'), name='swagger-ui'),
]

urlpatterns += router.urls