from django.db import models


class WhiteList(models.Model):
    """MAC地址白名单"""

    mac_address = models.CharField(max_length=17, unique=True, verbose_name="MAC地址")
    hostname = models.CharField(max_length=255, blank=True, verbose_name="主机名")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    description = models.TextField(blank=True, verbose_name="描述")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostname or 'Unknown'} - {self.mac_address}"

    class Meta:
        db_table = "white_list"
        ordering = ['id']
        verbose_name = "MAC地址白名单"
        verbose_name_plural = verbose_name