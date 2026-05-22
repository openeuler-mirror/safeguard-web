"""Network 相关 URL 配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views.network import (
    LoadBalancerViewSet,
    LBListenerViewSet,
    LBPoolViewSet,
    LBMemberViewSet,
    LBHealthMonitorViewSet,
)

router = DefaultRouter()
router.register(r'lbs', LoadBalancerViewSet, basename='lb')
router.register(r'listeners', LBListenerViewSet, basename='listener')
router.register(r'pools', LBPoolViewSet, basename='pool')
router.register(r'members', LBMemberViewSet, basename='member')
router.register(r'health-monitors', LBHealthMonitorViewSet, basename='health-monitor')

urlpatterns = [
    path('', include(router.urls)),
]