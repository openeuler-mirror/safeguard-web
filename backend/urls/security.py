"""Security 模块 URL 配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views.security import SafeguardViewSet

router = DefaultRouter()
router.register("safeguards", SafeguardViewSet, "safeguard")

urlpatterns = [
    path("", include(router.urls)),
]