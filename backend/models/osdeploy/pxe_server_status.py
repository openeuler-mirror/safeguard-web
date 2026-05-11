from django.db import models


class PXEServerStatus(models.Model):
    """PXE服务器状态"""

    STATUS_CHOICES = [
        ("active", "活跃"),
        ("inactive", "非活跃"),
        ("error", "错误"),
    ]

    server_ip = models.GenericIPAddressField(unique=True, verbose_name="服务器IP")
    interface = models.CharField(max_length=100, default="eth0", verbose_name="网卡")
    dhcp_range_start = models.GenericIPAddressField(verbose_name="DHCP起始IP")
    dhcp_range_end = models.GenericIPAddressField(verbose_name="DHCP结束IP")
    subnet = models.CharField(max_length=255, verbose_name="子网")
    gateway = models.GenericIPAddressField(verbose_name="网关")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="状态")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PXE Server {self.server_ip}"

    class Meta:
        db_table = "pxe_server_status"
        ordering = ['id']
        verbose_name = "PXE服务器状态"
        verbose_name_plural = verbose_name