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

    # CPU 相关字段
    cpu_usage = models.FloatField(
        null=True,
        blank=True,
        verbose_name='CPU使用率',
    )

    # 内存相关字段
    memory_total = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='总内存(字节)',
    )
    memory_used = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='已用内存(字节)',
    )
    memory_usage = models.FloatField(
        null=True,
        blank=True,
        verbose_name='内存使用率',
    )

    # 网络相关字段
    network_in = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='入站流量(字节)',
    )
    network_out = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='出站流量(字节)',
    )

    # 磁盘相关字段
    disk_read = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='磁盘读(字节)',
    )
    disk_write = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='磁盘写(字节)',
    )

    class Meta:
        db_table = 'host_monitor_data'
        ordering = ['-timestamp']
        verbose_name = '主机监控数据'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.host.hostname} - {self.timestamp}'
