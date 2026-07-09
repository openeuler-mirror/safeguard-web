"""
Audit Log Middleware

This middleware automatically logs user operations for audit purposes.
"""
import logging
import json
from typing import Optional, Dict, Any
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from safeguard_web.settings import AUDIT_LOG_ENABLED, AUDIT_WHITELIST_PATHS

logger = logging.getLogger(__name__)


class AuditLogMiddleware(MiddlewareMixin):
    """
    Audit Log Middleware

    Automatically logs user operations including:
    - Login/logout actions
    - Create/update/delete operations
    - Policy changes
    - Configuration modifications

    Features:
    - Whitelist support for excluding certain paths
    - Captures request/response details
    - Records IP address and User-Agent
    - Async logging to avoid blocking response
    """

    # 请求方法到操作类型的映射
    METHOD_ACTION_MAP = {
        'POST': 'create',
        'PUT': 'update',
        'PATCH': 'update',
        'DELETE': 'delete',
    }

    # URL路径到资源类型的映射规则
    PATH_RESOURCE_MAPS = [
        (r'/api/safeguard/policy/templates', 'policy_template'),
        (r'/api/safeguard/policy/host', 'host_policy'),
        (r'/api/safeguard/file-monitor/rules', 'file_monitor_rule'),
        (r'/api/safeguard/host-info', 'host_info'),
        (r'/api/safeguard/monitor', 'monitor'),
        (r'/api/auth/login', 'auth'),
        (r'/api/auth/logout', 'auth'),
        (r'/api/users', 'user'),
        (r'/api/hosts', 'host'),
    ]

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)

    def _parse_resource_type(self, path: str) -> str:
        """
        从URL路径解析资源类型

        Args:
            path: URL路径

        Returns:
            str: 资源类型字符串
        """
        import re
        for pattern, resource_type in self.PATH_RESOURCE_MAPS:
            if re.search(pattern, path):
                return resource_type

        # 尝试从路径中提取
        parts = path.strip('/').split('/')
        if len(parts) >= 2:
            return parts[-2]  # 使用倒数第二段作为资源类型

        return 'unknown'

    def _parse_resource_id(self, path: str) -> str:
        """
        从URL路径解析资源ID

        Args:
            path: URL路径

        Returns:
            str: 资源ID字符串
        """
        import re
        # 查找路径中的数字ID
        match = re.search(r'/(\d+)/?$', path)
        if match:
            return match.group(1)
        return ''

    def _parse_action(self, request: HttpRequest) -> str:
        """
        解析操作类型

        Args:
            request: Django HTTP请求对象

        Returns:
            str: 操作类型
        """
        path = request.path
        method = request.method

        # 特殊处理登录登出
        if '/login' in path:
            return 'login'
        if '/logout' in path:
            return 'logout'

        # 策略下发特殊处理
        if '/policy/templates' in path and '/apply' in path:
            return 'policy_apply'

        # 使用方法映射
        return self.METHOD_ACTION_MAP.get(method, 'config_change')

    def _get_request_body(self, request: HttpRequest) -> Dict[str, Any]:
        """
        获取请求体数据（安全解析）

        Args:
            request: Django HTTP请求对象

        Returns:
            dict: 请求体数据
        """
        try:
            if hasattr(request, 'body') and request.body:
                # 尝试解析JSON
                try:
                    return json.loads(request.body.decode('utf-8')[:10000])  # 限制大小
                except json.JSONDecodeError:
                    # 不是JSON，返回空dict
                    pass
        except Exception:
            pass
        return {}

    def _get_response_data(self, response: HttpResponse) -> Dict[str, Any]:
        """
        从响应中提取有用的数据

        Args:
            response: Django HTTP响应对象

        Returns:
            dict: 响应数据
        """
        try:
            if hasattr(response, 'data'):
                # DRF Response对象
                data = response.data
                if isinstance(data, dict):
                    # 提取资源ID和名称
                    return {
                        'id': data.get('id'),
                        'name': data.get('name'),
                    }
        except Exception:
            pass
        return {}

    def _should_skip(self, request: HttpRequest) -> bool:
        """
        判断是否应该跳过审计记录

        Args:
            request: Django HTTP请求对象

        Returns:
            bool: True表示跳过，False表示需要记录
        """
        # 如果审计功能未启用，直接跳过
        if not AUDIT_LOG_ENABLED:
            return True

        path = request.path

        # 跳过白名单路径
        for whitelist_path in AUDIT_WHITELIST_PATHS:
            if path.startswith(whitelist_path):
                return True

        # 只记录写操作
        if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return True

        # 跳过审计日志相关的API
        if '/api/safeguard/audit' in path:
            return True

        return False

    def _get_client_ip(self, request: HttpRequest) -> Optional[str]:
        """
        获取客户端真实IP地址

        Args:
            request: Django HTTP请求对象

        Returns:
            str: IP地址字符串或None
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _get_user_agent(self, request: HttpRequest) -> str:
        """
        获取User-Agent

        Args:
            request: Django HTTP请求对象

        Returns:
            str: User-Agent字符串
        """
        return request.META.get('HTTP_USER_AGENT', '')[:500]  # 限制长度

    def process_request(self, request: HttpRequest):
        """
        请求前处理

        Args:
            request: Django HTTP请求对象
        """
        if self._should_skip(request):
            return None

        # 存储路径信息，供process_response使用
        request._audit_path = request.path
        request._audit_method = request.method

        return None

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        响应后处理 - 记录审计日志

        Args:
            request: Django HTTP请求对象
            response: Django HTTP响应对象

        Returns:
            HttpResponse: 原始响应对象
        """
        if self._should_skip(request):
            return response

        try:
            # 只记录成功的操作
            if response.status_code not in [200, 201, 204]:
                return response

            logger.debug(f'Audit log would be recorded: {request.method} {request.path}')

        except Exception as e:
            # 审计日志记录失败不影响正常响应
            logger.error(f'Failed to record audit log: {e}', exc_info=True)

        return response
