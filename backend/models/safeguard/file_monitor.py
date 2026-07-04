from django.db import models
from backend.models.host import Host


class FileMonitorRule(models.Model):
    """文件监控规则"""

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

    class Meta:
        db_table = 'file_monitor_rules'
        ordering = ['-id']
        verbose_name = '文件监控规则'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.host.hostname} - {self.path}'
