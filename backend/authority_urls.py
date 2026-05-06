from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.authority_views import AuthorityViewSet, MenuViewSet

router = DefaultRouter()
router.register(r'authorities', AuthorityViewSet, basename='authority')
router.register(r'menus', MenuViewSet, basename='menu')

urlpatterns = [
    path('', include(router.urls)),
]
