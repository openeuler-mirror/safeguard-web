"""OSmigrate URL 配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views.osmigrate.migrate import MigrateViewSet

router = DefaultRouter()
router.register(r"migrates", MigrateViewSet, basename="migrate")

urlpatterns = [
    path("", include(router.urls)),
]
