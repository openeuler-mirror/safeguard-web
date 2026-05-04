from django.contrib import admin
from django.urls import path,include
from rest_framework import routers
from backend import views
from rest_framework.schemas import get_schema_view
from drf_yasg.renderers import SwaggerUIRenderer, OpenAPIRenderer

from backend.views import UsersViewSet

schema_view = get_schema_view(title='API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet, basename="users")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include(router.urls)),
    path('api-auth/',include('rest_framework.urls',namespace='rest_framework')),

    path('docs/',schema_view,name='docs'),
]

urlpatterns += router.urls