from django.db import models


class LBListener(models.Model):
    """监听器"""

    PROTOCOL_CHOICES = [
        ("tcp", "TCP"),
        ("http", "HTTP"),
        ("https", "HTTPS"),
    ]

    loadbalancer = models.ForeignKey(
        "LoadBalancer",
        related_name="listeners",
        on_delete=models.CASCADE,
        verbose_name="负载均衡器"
    )
    protocol = models.CharField(max_length=10, choices=PROTOCOL_CHOICES, verbose_name="协议")
    port = models.IntegerField(verbose_name="端口")
    name = models.CharField(max_length=100, blank=True, verbose_name="名称")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name or 'Listener'} - {self.protocol}:{self.port}"

    class Meta:
        db_table = "lb_listener"
        ordering = ['-created_at']
        verbose_name = "监听器"
        verbose_name_plural = verbose_name