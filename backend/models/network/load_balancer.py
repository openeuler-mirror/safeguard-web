from django.db import models


class LoadBalancer(models.Model):
    """负载均衡器"""

    ALGORITHM_CHOICES = [
        ("round_robin", "轮询"),
        ("least_conn", "最少连接"),
        ("source", "源IP"),
    ]

    STATUS_CHOICES = [
        ("active", "活跃"),
        ("inactive", "未激活"),
        ("error", "异常"),
    ]

    name = models.CharField(max_length=100, verbose_name="名称")
    vip_address = models.GenericIPAddressField(verbose_name="VIP地址")
    port = models.IntegerField(default=80, verbose_name="端口")
    algorithm = models.CharField(max_length=20, choices=ALGORITHM_CHOICES, default="round_robin", verbose_name="负载算法")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="状态")
    description = models.TextField(blank=True, verbose_name="描述")
    created_by = models.ForeignKey(
        'backend.Users', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="创建者"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.vip_address}"

    class Meta:
        db_table = "load_balancer"
        ordering = ['-created_at']
        verbose_name = "负载均衡器"
        verbose_name_plural = verbose_name