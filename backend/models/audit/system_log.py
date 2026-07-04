from django.db import models
from backend.models.host import Host


class SystemLog(models.Model):
    """系统日志"""

    LEVEL_CHOICES = [
        ('debug', 'DEBUG'),
        ('info', 'INFO'),
        ('warning', 'WARNING'),
        ('error', 'ERROR'),
        ('critical', 'CRITICAL'),
    ]

    host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
        related_name='system_logs',
        verbose_name='主机',
    )
    source = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='日志来源',
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='info',
        verbose_name='日志级别',
    )
    message = models.TextField(
        verbose_name='日志消息',
    )
    timestamp = models.DateTimeField(
        db_index=True,
        verbose_name='日志时间',
    )
    raw_log = models.TextField(
        blank=True,
        verbose_name='原始日志',
    )
    parsed_fields = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='解析后的字段',
    )
    collected_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='采集时间',
    )

    class Meta:
        db_table = 'system_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['host', 'timestamp']),
            models.Index(fields=['level']),
        ]
        verbose_name = '系统日志'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.level} - {self.message[:50]}'
