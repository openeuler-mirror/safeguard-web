from django.db import models
from backend.models.host import Host


class FileMonitorRule(models.Model):
    """文件监控规则"""

    MONITOR_TYPE_CHOICES = [
        ('file', '文件'),
        ('dir', '目录'),
    ]

    host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
        related_name='file_monitor_rules',
        verbose_name='主机',
    )
    path = models.CharField(
        max_length=500,
        verbose_name='监控路径',
    )
    monitor_type = models.CharField(
        max_length=20,
        choices=MONITOR_TYPE_CHOICES,
        default='file',
        verbose_name='监控类型',
    )

    # 监控事件类型
    watch_create = models.BooleanField(
        default=True,
        verbose_name='监控创建',
    )
    watch_modify = models.BooleanField(
        default=True,
        verbose_name='监控修改',
    )
    watch_delete = models.BooleanField(
        default=True,
        verbose_name='监控删除',
    )
    watch_access = models.BooleanField(
        default=False,
        verbose_name='监控访问',
    )
    watch_perm = models.BooleanField(
        default=True,
        verbose_name='监控权限变更',
    )

    recursive = models.BooleanField(
        default=False,
        verbose_name='递归监控',
    )
    includes = models.JSONField(
        default=list,
        blank=True,
        verbose_name='包含规则',
    )
    excludes = models.JSONField(
        default=list,
        blank=True,
        verbose_name='排除规则',
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name='启用',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
    )

    class Meta:
        db_table = 'file_monitor_rules'
        ordering = ['-created_at']
        verbose_name = '文件监控规则'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.host.hostname} - {self.path}'


class FileMonitorState(models.Model):
    """文件监控状态，用于跟踪文件变化"""
    rule = models.ForeignKey(
        FileMonitorRule,
        on_delete=models.CASCADE,
        related_name='states',
        verbose_name='监控规则',
    )
    path = models.CharField(
        max_length=500,
        verbose_name='文件路径',
    )
    # 文件关键属性快照
    mtime = models.DateTimeField(
        verbose_name='最后修改时间',
    )
    ctime = models.DateTimeField(
        verbose_name='最后状态变更时间',
    )
    size = models.BigIntegerField(
        verbose_name='文件大小',
    )
    uid = models.IntegerField(
        verbose_name='用户ID',
    )
    gid = models.IntegerField(
        verbose_name='组ID',
    )
    mode = models.CharField(
        max_length=10,
        verbose_name='权限模式',
    )
    file_hash = models.CharField(
        max_length=64,
        blank=True,
        verbose_name='文件哈希',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
    )

    class Meta:
        db_table = 'file_monitor_states'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['rule', 'path']),
        ]
        verbose_name = '文件监控状态'
        verbose_name_plural = verbose_name
        unique_together = ('rule', 'path')

    def __str__(self):
        return f'{self.rule.id} - {self.path}'


class FileMonitorEvent(models.Model):
    """文件监控事件"""

    host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
        related_name='file_monitor_events',
        verbose_name='主机',
    )
    rule = models.ForeignKey(
        FileMonitorRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        verbose_name='触发规则',
    )
    event_type = models.CharField(
        max_length=50,
        verbose_name='事件类型',
    )
    path = models.CharField(
        max_length=500,
        verbose_name='文件路径',
    )
    process_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='进程名称',
    )
    process_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='进程ID',
    )
    user = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='操作用户',
    )
    timestamp = models.DateTimeField(
        db_index=True,
        verbose_name='事件时间',
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='详细信息',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
    )

    class Meta:
        db_table = 'file_monitor_events'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['host', 'timestamp']),
            models.Index(fields=['event_type']),
        ]
        verbose_name = '文件监控事件'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.event_type} - {self.path}'
