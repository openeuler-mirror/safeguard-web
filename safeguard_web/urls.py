from django.contrib import admin
from django.urls import path,include
from rest_framework import routers, permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from backend.views.user import UsersViewSet
from backend.views.auth import (
    LoginView,
    RegisterView,
    SendVerificationCodeView,
    VerifyCodeView,
    ForgotPasswordView,
    ResetPasswordView,
    LocalVerifyView,
)

router = routers.DefaultRouter()
router.register(r'api/users', UsersViewSet, basename="users")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/send-code/', SendVerificationCodeView.as_view(), name='send-code'),
    path('api/auth/verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('api/auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('api/auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('api/auth/local-verify/<str:email>/<str:code>/', LocalVerifyView.as_view(), name='local-verify'),
    path('api/authority/', include('backend.authority_urls')),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls',namespace='rest_framework')),

    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[permissions.AllowAny],  authentication_classes=[]), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(permission_classes=[permissions.AllowAny],  authentication_classes=[], url_name='schema'), name='swagger-ui'),
]

urlpatterns += router.urls