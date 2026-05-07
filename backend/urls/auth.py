"""认证相关 URL 配置"""
from django.urls import path
from backend.views.auth import (
    LoginView,
    RegisterView,
    SendVerificationCodeView,
    VerifyCodeView,
    ForgotPasswordView,
    ResetPasswordView,
    LocalVerifyView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('send-code/', SendVerificationCodeView.as_view(), name='send-code'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('local-verify/<str:email>/<str:code>/', LocalVerifyView.as_view(), name='local-verify'),
]
