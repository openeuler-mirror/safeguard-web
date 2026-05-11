from django.db import models


class OutIpSN(models.Model):
    """出口IP序列号"""

    mac_address = models.CharField(max_length=17, unique=True, verbose_name="MAC地址")
    sn = models.CharField(max_length=100, verbose_name="序列号")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.mac_address} - {self.sn}"

    class Meta:
        db_table = "out_ip_sn"
        ordering = ['id']
        verbose_name = "出口IP序列号"
        verbose_name_plural = verbose_name