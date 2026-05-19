from django.db import models


class LBPool(models.Model):
    """后端池"""

    PROTOCOL_CHOICES = [
        ("tcp", "TCP"),
        ("http", "HTTP"),
        ("https", "HTTPS"),
    ]

    name = models.CharField(max_length=100, verbose_name="名称")
    loadbalancer = models.ForeignKey(
        "LoadBalancer",
        on_delete=models.CASCADE,
        verbose_name="负载均衡器"
    )
    protocol = models.CharField(max_length=10, choices=PROTOCOL_CHOICES, verbose_name="协议")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.protocol}"

    class Meta:
        db_table = "lb_pool"
        ordering = ['-created_at']
        verbose_name = "后端池"
        verbose_name_plural = verbose_name