from django.db import models
from backend.models.host import Host


class SafeguardPolicyTemplate(models.Model):
    """Safeguard 策略模板"""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='模板名称',
    )
    description = models.TextField(
        blank=True,
        verbose_name='描述',
    )

    class Meta:
        db_table = 'safeguard_policy_templates'
        ordering = ['-id']
        verbose_name = '策略模板'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
