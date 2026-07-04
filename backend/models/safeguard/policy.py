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
