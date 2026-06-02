"""RPC URL 配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views.rpc.file import FileViewSet

router = DefaultRouter()
router.register(r"rpc/files", FileViewSet, basename="rpc-file")

urlpatterns = [
    path("", include(router.urls)),
]
