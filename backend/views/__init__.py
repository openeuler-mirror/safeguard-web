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
from backend.views.host import ClusterViewSet, HostViewSet, VMViewSet
from backend.views.task import TaskViewSet
from backend.views.osmigrate import MigrateViewSet

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
    'HostViewSet',
    'VMViewSet',
    # Task views
    'TaskViewSet',
    # OSmigrate views
    'MigrateViewSet',
]
