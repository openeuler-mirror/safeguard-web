from django.db import models
from backend.models.host import Host


class SafeguardPolicyTemplate(models.Model):
    """Safeguard 策略模板"""

    TEMPLATE_TYPE_CHOICES = [
        ('general', '通用防护'),
        ('business', '业务服务器'),
        ('audit', '审计模式'),
        ('custom', '自定义'),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='模板名称',
    )
    description = models.TextField(
        blank=True,
        verbose_name='描述',
    )
    template_type = models.CharField(
        max_length=50,
        choices=TEMPLATE_TYPE_CHOICES,
        default='custom',
        verbose_name='模板类型',
    )
    is_builtin = models.BooleanField(
        default=False,
        verbose_name='内置模板',
    )
    config = models.JSONField(
        default=dict,
        verbose_name='策略配置',
    )
    created_by = models.ForeignKey(
        'backend.Users',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='创建者',
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
        db_table = 'safeguard_policy_templates'
        ordering = ['-created_at']
        verbose_name = '策略模板'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class HostSafeguardPolicy(models.Model):
    """主机 Safeguard 策略"""

    STATUS_CHOICES = [
        ('pending', '待下发'),
        ('applying', '下发中'),
        ('active', '已生效'),
        ('failed', '下发失败'),
    ]

    host = models.OneToOneField(
        Host,
        on_delete=models.CASCADE,
        related_name='safeguard_policy',
        verbose_name='主机',
    )
    template = models.ForeignKey(
        SafeguardPolicyTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='关联模板',
    )
    config = models.JSONField(
        default=dict,
        verbose_name='实际生效配置',
    )
    config_version = models.IntegerField(
        default=1,
        verbose_name='配置版本',
    )
    applied_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='应用时间',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态',
    )
    last_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后同步时间',
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
        db_table = 'host_safeguard_policies'
        verbose_name = '主机策略'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.host.hostname} - {self.status}'


class PolicyApplyTask(models.Model):
    """策略下发任务"""

    TASK_TYPE_CHOICES = [
        ('apply', '下发'),
        ('rollback', '回滚'),
    ]
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '执行中'),
        ('success', '成功'),
        ('failed', '失败'),
    ]

    host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
        related_name='policy_tasks',
        verbose_name='主机',
    )
    policy = models.ForeignKey(
        HostSafeguardPolicy,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='策略',
    )
    task_type = models.CharField(
        max_length=20,
        choices=TASK_TYPE_CHOICES,
        verbose_name='任务类型',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态',
    )
    message = models.TextField(
        blank=True,
        verbose_name='消息',
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='开始时间',
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='完成时间',
    )
    created_by = models.ForeignKey(
        'backend.Users',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='创建者',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
    )

    class Meta:
        db_table = 'policy_apply_tasks'
        ordering = ['-created_at']
        verbose_name = '策略下发任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.host.hostname} - {self.task_type} - {self.status}'
