"""主机相关 URL 配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views.host import ClusterViewSet

router = DefaultRouter()
router.register(r'clusters', ClusterViewSet, basename='cluster')

urlpatterns = [
    path('', include(router.urls)),
]