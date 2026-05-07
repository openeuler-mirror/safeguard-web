# Permissions module
from backend.permissions.base import DataScopePermission
from backend.permissions.authority import IsSuperAdmin, IsAdmin, AuthorityPermission

__all__ = [
    'DataScopePermission',
    'IsSuperAdmin',
    'IsAdmin',
    'AuthorityPermission',
]
