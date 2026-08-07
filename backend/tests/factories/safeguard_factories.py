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


class HostMonitorDataFactory:
    """主机监控数据工厂"""

    @staticmethod
    def create(host=None, cpu_usage=50.0, load_1m=1.0, load_5m=0.8, load_15m=0.5,
               memory_total=8*1024*1024*1024, memory_used=4*1024*1024*1024,
               memory_usage=50.0, network_in=1024, network_out=512,
               disk_read=2048, disk_write=1024, **kwargs):
        """创建监控数据"""
        return HostMonitorData.objects.create(
            host=host,
            cpu_usage=cpu_usage,
            load_1m=load_1m,
            load_5m=load_5m,
            load_15m=load_15m,
            memory_total=memory_total,
            memory_used=memory_used,
            memory_usage=memory_usage,
            network_in=network_in,
            network_out=network_out,
            disk_read=disk_read,
            disk_write=disk_write,
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建监控数据"""
        data_list = []
        for i in range(count):
            data_list.append(HostMonitorDataFactory.create(**kwargs))
        return data_list


class FileMonitorRuleFactory:
    """文件监控规则工厂"""

    @staticmethod
    def create(host=None, path="/etc/passwd", monitor_type="file",
               watch_create=True, watch_modify=True, watch_delete=True,
               watch_access=False, watch_perm=True, recursive=False,
               includes=None, excludes=None, enabled=True, **kwargs):
        """创建文件监控规则"""
        return FileMonitorRule.objects.create(
            host=host,
            path=path,
            monitor_type=monitor_type,
            watch_create=watch_create,
            watch_modify=watch_modify,
            watch_delete=watch_delete,
            watch_access=watch_access,
            watch_perm=watch_perm,
            recursive=recursive,
            includes=includes or [],
            excludes=excludes or [],
            enabled=enabled,
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建监控规则"""
        rules = []
        for i in range(count):
            rules.append(FileMonitorRuleFactory.create(**kwargs))
        return rules


class FileMonitorEventFactory:
    """文件监控事件工厂"""

    @staticmethod
    def create(host=None, rule=None, event_type="modify", path="/etc/passwd",
               process_name=None, process_id=None, user=None, timestamp=None,
               details=None, **kwargs):
        """创建文件监控事件"""
        if timestamp is None:
            timestamp = timezone.now()
        return FileMonitorEvent.objects.create(
            host=host,
            rule=rule,
            event_type=event_type,
            path=path,
            process_name=process_name,
            process_id=process_id,
            user=user,
            timestamp=timestamp,
            details=details or {},
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建事件"""
        events = []
        for i in range(count):
            events.append(FileMonitorEventFactory.create(**kwargs))
        return events


class AuditLogFactory:
    """审计日志工厂"""

    @staticmethod
    def create(user=None, action="create", resource_type="host", resource_id="1",
                resource_name="test-host", action_details=None,
                old_value=None, new_value=None, ip_address=None,
                user_agent=None, status="success", error_message="", **kwargs):
        """创建审计日志"""
        return AuditLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            action_details=action_details or {},
            old_value=old_value or {},
            new_value=new_value or {},
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message,
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建审计日志"""
        logs = []
        for i in range(count):
            logs.append(AuditLogFactory.create(**kwargs))
        return logs

    @staticmethod
    def create_login(**kwargs):
        """创建登录审计日志"""
        return AuditLogFactory.create(action="login", **kwargs)

    @staticmethod
    def create_failed(**kwargs):
        """创建失败的审计日志"""
        return AuditLogFactory.create(status="failed", **kwargs)


class SystemLogFactory:
    """系统日志工厂"""

    @staticmethod
    def create(host=None, source="system", level="info", message="System message",
               timestamp=None, raw_log="", parsed_fields=None, **kwargs):
        """创建系统日志"""
        if timestamp is None:
            timestamp = timezone.now()
        return SystemLog.objects.create(
            host=host,
            source=source,
            level=level,
            message=message,
            timestamp=timestamp,
            raw_log=raw_log,
            parsed_fields=parsed_fields or {},
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建系统日志"""
        logs = []
        for i in range(count):
            logs.append(SystemLogFactory.create(**kwargs))
        return logs

    @staticmethod
    def create_error(**kwargs):
        """创建错误日志"""
        return SystemLogFactory.create(level="error", **kwargs)

    @staticmethod
    def create_warning(**kwargs):
        """创建警告日志"""
        return SystemLogFactory.create(level="warning", **kwargs)
