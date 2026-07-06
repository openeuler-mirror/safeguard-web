"""Safeguard 相关 URL 配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views.safeguard.host_info import HostInfoViewSet
from backend.views.safeguard.monitor import HostMonitorDataViewSet
from backend.views.safeguard.policy import (
    SafeguardPolicyTemplateViewSet,
    HostSafeguardPolicyViewSet,
    PolicyApplyTaskViewSet,
)
from backend.views.safeguard.file_monitor import (
    FileMonitorRuleViewSet,
    FileMonitorEventViewSet,
)
from backend.views.safeguard.audit import AuditLogViewSet

router = DefaultRouter()
router.register(r'host-info', HostInfoViewSet, basename='host-info')
router.register(r'monitor-data', HostMonitorDataViewSet, basename='monitor-data')
router.register(r'policy-templates', SafeguardPolicyTemplateViewSet, basename='policy-template')
router.register(r'host-policies', HostSafeguardPolicyViewSet, basename='host-policy')
router.register(r'policy-tasks', PolicyApplyTaskViewSet, basename='policy-task')
router.register(r'file-monitor-rules', FileMonitorRuleViewSet, basename='file-monitor-rule')
router.register(r'file-monitor-events', FileMonitorEventViewSet, basename='file-monitor-event')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('', include(router.urls)),
]
