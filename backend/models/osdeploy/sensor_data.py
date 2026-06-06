from django.db import models


class SensorData(models.Model):
    """Sensor 上报数据"""
    ip = models.GenericIPAddressField(verbose_name="客户端IP")
    function = models.CharField(max_length=255, verbose_name="功能标识")
    data = models.TextField(verbose_name="上报数据")
    time = models.CharField(max_length=50, verbose_name="上报时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="接收时间")

    class Meta:
        db_table = "sensor"
        verbose_name = "Sensor数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.ip} - {self.function}"
