from django.db import models


class LBHealthMonitor(models.Model):
    """健康检查"""

    MONITOR_TYPE_CHOICES = [
        ("tcp", "TCP"),
        ("http", "HTTP"),
        ("ping", "PING"),
    ]

    pool = models.OneToOneField(
        "LBPool",
        on_delete=models.CASCADE,
        verbose_name="后端池"
    )
    monitor_type = models.CharField(max_length=10, choices=MONITOR_TYPE_CHOICES, verbose_name="检查类型")
    interval = models.IntegerField(default=5, verbose_name="检查间隔(秒)")
    timeout = models.IntegerField(default=3, verbose_name="超时(秒)")
    retry = models.IntegerField(default=3, verbose_name="重试次数")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Monitor for {self.pool.name} - {self.monitor_type}"

    class Meta:
        db_table = "lb_health_monitor"
        ordering = ['-created_at']
        verbose_name = "健康检查"
        verbose_name_plural = verbose_name