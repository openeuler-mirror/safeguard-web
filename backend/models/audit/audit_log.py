from django.db import models


class AuditLog(models.Model):
    """审计日志"""

    ACTION_CHOICES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('policy_apply', '策略下发'),
        ('config_change', '配置变更'),
    ]

    user = models.ForeignKey(
        'backend.Users',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='用户',
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        verbose_name='操作类型',
    )
    resource_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='资源类型',
    )
    resource_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='资源ID',
    )
    resource_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='资源名称',
    )
    action_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='操作详情',
    )
    old_value = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='变更前值',
    )
    new_value = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='变更后值',
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='客户端IP',
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='User-Agent',
    )
    status = models.CharField(
        max_length=20,
        choices=[('success', '成功'), ('failed', '失败')],
        default='success',
        verbose_name='状态',
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='错误消息',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
    )

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        verbose_name = '审计日志'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.action} - {self.resource_name}'
