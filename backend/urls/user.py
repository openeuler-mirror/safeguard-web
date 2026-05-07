"""用户相关 URL 配置"""
from django.urls import path, include
from rest_framework import routers
from backend.views.user import UsersViewSet

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
