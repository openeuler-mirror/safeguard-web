# Views module
from backend.views.user import UsersViewSet
from backend.views.auth import (
    LoginView,
    RegisterView,
    SendVerificationCodeView,
    VerifyCodeView,
    LocalVerifyView,
    ForgotPasswordView,
    ResetPasswordView,
)
from backend.views.authority import AuthorityViewSet, MenuViewSet
from backend.views.host import ClusterViewSet

__all__ = [
    # User views
    'UsersViewSet',
    # Auth views
    'LoginView',
    'RegisterView',
    'SendVerificationCodeView',
    'VerifyCodeView',
    'LocalVerifyView',
    'ForgotPasswordView',
    'ResetPasswordView',
    # Authority views
    'AuthorityViewSet',
    'MenuViewSet',
    # Host views
    'ClusterViewSet',
]
