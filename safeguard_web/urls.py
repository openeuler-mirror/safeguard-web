from django.contrib import admin
from django.urls import path,include
from rest_framework import routers, permissions
from backend import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from backend.views import UsersViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="safeguard-web api",
        default_version="1.0.0",
        description="接口文档",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,)
)

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet, basename="users")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include(router.urls)),
    path('api-auth/',include('rest_framework.urls',namespace='rest_framework')),

     # Swagger UI
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # 可选：JSON 格式 schema
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

urlpatterns += router.urls