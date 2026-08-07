"""安全防护相关测试数据工厂"""
import uuid
from django.utils import timezone
from backend.models.safeguard.monitor import HostMonitorData
from backend.models.safeguard.file_monitor import FileMonitorRule, FileMonitorEvent
from backend.models.safeguard.policy import (
    SafeguardPolicyTemplate,
    HostSafeguardPolicy,
    PolicyApplyTask,
)
from backend.models.audit.audit_log import AuditLog
from backend.models.audit.system_log import SystemLog


class SafeguardPolicyTemplateFactory:
    """安全策略模板工厂"""

    @staticmethod
    def create(name=None, template_type="custom", is_builtin=False, config=None, created_by=None, **kwargs):
        """创建策略模板"""
        return SafeguardPolicyTemplate.objects.create(
            name=name or f"policy-{uuid.uuid4().hex[:6]}",
            template_type=template_type,
            is_builtin=is_builtin,
            config=config or {"rules": []},
            created_by=created_by,
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建策略模板"""
        templates = []
        for i in range(count):
            templates.append(SafeguardPolicyTemplateFactory.create(**kwargs))
        return templates

    @staticmethod
    def create_general(**kwargs):
        """创建通用防护模板"""
        return SafeguardPolicyTemplateFactory.create(template_type="general", **kwargs)

    @staticmethod
    def create_builtin(**kwargs):
        """创建内置模板"""
        return SafeguardPolicyTemplateFactory.create(is_builtin=True, **kwargs)


class HostSafeguardPolicyFactory:
    """主机安全策略工厂"""

    @staticmethod
    def create(host=None, template=None, config=None, config_version=1, status="pending", **kwargs):
        """创建主机策略"""
        return HostSafeguardPolicy.objects.create(
            host=host,
            template=template,
            config=config or {},
            config_version=config_version,
            status=status,
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建主机策略"""
        policies = []
        for i in range(count):
            policies.append(HostSafeguardPolicyFactory.create(**kwargs))
        return policies

    @staticmethod
    def create_active(**kwargs):
        """创建已生效策略"""
        return HostSafeguardPolicyFactory.create(status="active", **kwargs)


class PolicyApplyTaskFactory:
    """策略下发任务工厂"""

    @staticmethod
    def create(host=None, policy=None, task_type="apply", status="pending", created_by=None, **kwargs):
        """创建策略任务"""
        return PolicyApplyTask.objects.create(
            host=host,
            policy=policy,
            task_type=task_type,
            status=status,
            created_by=created_by,
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建任务"""
        tasks = []
        for i in range(count):
            tasks.append(PolicyApplyTaskFactory.create(**kwargs))
        return tasks

    @staticmethod
    def create_running(**kwargs):
        """创建运行中任务"""
        return PolicyApplyTaskFactory.create(status="running", **kwargs)

    @staticmethod
    def create_success(**kwargs):
        """创建成功任务"""
        return PolicyApplyTaskFactory.create(status="success", **kwargs)

