# 保持向后兼容的导入
# 所有 authority views 已移动到 backend/views/authority.py
from backend.views.authority import AuthorityViewSet, MenuViewSet

__all__ = [
    'AuthorityViewSet',
    'MenuViewSet',
]
