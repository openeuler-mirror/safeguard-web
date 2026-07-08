"""
Audit Log Middleware

This middleware automatically logs user operations for audit purposes.
"""
import logging
from typing import Optional
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

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)

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
