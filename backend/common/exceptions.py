"""
自定义异常类

用于服务层抛出业务异常，包含错误码和错误信息。
"""
from backend.common.errcodes import ErrCode, get_errmsg


class ServiceError(Exception):
    """服务层基础异常"""

    def __init__(self, err_code: int, err_msg: str = None):
        self.err_code = err_code
        self.err_msg = err_msg or get_errmsg(err_code)
        super().__init__(self.err_msg)


class HostNotFoundError(ServiceError):
    """主机不存在"""

    def __init__(self, host_id: int):
        super().__init__(ErrCode.HOST_NOT_FOUND, f"主机 {host_id} 不存在")


class VMNotFoundError(ServiceError):
    """虚拟机不存在"""

    def __init__(self, vm_id: int):
        super().__init__(ErrCode.VM_NOT_FOUND, f"虚拟机 {vm_id} 不存在")


class ClusterNotFoundError(ServiceError):
    """集群不存在"""

    def __init__(self, cluster_id: int):
        super().__init__(ErrCode.CLUSTER_NOT_FOUND, f"集群 {cluster_id} 不存在")


class PolicyTemplateNotFoundError(ServiceError):
    """策略模板不存在"""

    def __init__(self, template_id: int):
        super().__init__(ErrCode.NOT_FOUND, f"策略模板 {template_id} 不存在")


class HostPolicyNotFoundError(ServiceError):
    """主机策略不存在"""

    def __init__(self, host_id: int):
        super().__init__(ErrCode.NOT_FOUND, f"主机 {host_id} 的策略不存在")


class TaskNotFoundError(ServiceError):
    """任务不存在"""

    def __init__(self, task_id: int):
        super().__init__(ErrCode.NOT_FOUND, f"任务 {task_id} 不存在")


class JobNotFoundError(ServiceError):
    """任务不存在（用于 OS Deploy）"""

    def __init__(self, job_id: str):
        super().__init__(ErrCode.NOT_FOUND, f"任务不存在: {job_id}")


class ConfigGenerationError(ServiceError):
    """配置文件生成失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class HardwareCollectError(ServiceError):
    """硬件信息采集失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.HOST_HARDWARE_COLLECT_FAILED, message)


class LLDCollectError(ServiceError):
    """LLDP 信息采集失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.HOST_LLDP_COLLECT_FAILED, message)


class PasswordUpdateError(ServiceError):
    """密码更新失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.HOST_PASSWORD_UPDATE_FAILED, message)


class VMOperationError(ServiceError):
    """虚拟机操作失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.VM_OPERATION_FAILED, message)


class OperationError(ServiceError):
    """通用操作失败异常"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class HostConnectionError(ServiceError):
    """主机连接失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class FileMonitorRuleNotFoundError(ServiceError):
    """文件监控规则不存在"""

    def __init__(self, rule_id: int):
        super().__init__(ErrCode.NOT_FOUND, f"文件监控规则 {rule_id} 不存在")


class AuditLogCreateError(ServiceError):
    """审计日志创建失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class FileMonitorRuleCreateError(ServiceError):
    """文件监控规则创建失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class FileMonitorEventCollectError(ServiceError):
    """文件监控事件收集失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class SystemLogCollectError(ServiceError):
    """系统日志收集失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class HostInfoCollectError(ServiceError):
    """主机信息收集失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class MonitorDataSaveError(ServiceError):
    """监控数据保存失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class MonitorHistoryQueryError(ServiceError):
    """监控历史查询失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class MonitorCollectError(ServiceError):
    """监控数据采集失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class PolicyApplyError(ServiceError):
    """策略应用失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class HostImportError(ServiceError):
    """主机导入失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)


class RemoteCommandError(ServiceError):
    """远程命令执行失败"""

    def __init__(self, message: str):
        super().__init__(ErrCode.OPERATION_FAILED, message)
