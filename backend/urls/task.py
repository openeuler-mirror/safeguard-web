"""Task 模块 URL 配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views.task import TaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
]
