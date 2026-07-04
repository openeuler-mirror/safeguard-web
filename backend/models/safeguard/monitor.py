from django.db import models
from backend.models.host import Host


class HostMonitorData(models.Model):
    """主机监控数据"""

    host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
        related_name='monitor_data',
        verbose_name='主机',
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='采集时间',
    )

    class Meta:
        db_table = 'host_monitor_data'
        ordering = ['-timestamp']
        verbose_name = '主机监控数据'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.host.hostname} - {self.timestamp}'
