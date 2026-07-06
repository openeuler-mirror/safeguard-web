"""Safeguard 视图模块"""
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
from backend.views.safeguard.audit import AuditLogViewSet, SystemLogViewSet
from backend.views.safeguard.host_info import HostInfoViewSet

__all__ = [
    'HostMonitorDataViewSet',
    'SafeguardPolicyTemplateViewSet',
    'HostSafeguardPolicyViewSet',
    'PolicyApplyTaskViewSet',
    'FileMonitorRuleViewSet',
    'FileMonitorEventViewSet',
    'AuditLogViewSet',
    'SystemLogViewSet',
    'HostInfoViewSet',
]
