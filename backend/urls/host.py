"""主机相关 URL 配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views.host import ClusterViewSet, HostViewSet, VMViewSet

router = DefaultRouter()
router.register(r'clusters', ClusterViewSet, basename='cluster')
router.register(r'hosts', HostViewSet, basename='host')
router.register(r'vms', VMViewSet, basename='vm')

urlpatterns = [
    path('', include(router.urls)),
]