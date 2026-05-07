from django.db import models


class Hosts(models.Model):
    """主机/服务器模型"""
    ipaddress = models.CharField(max_length=50)
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    port = models.IntegerField(null=True, blank=True)
    cluster = models.CharField(max_length=50)

    def __str__(self):
        return self.ipaddress


class Cluster(models.Model):
    """集群"""
    name = models.CharField(max_length=100, unique=True, verbose_name="集群名称")
    description = models.TextField(blank=True, verbose_name="描述")
    vcenter_id = models.CharField(max_length=100, blank=True, verbose_name="vCenter ID")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "clusters"
        ordering = ['id']
        verbose_name = "集群"
        verbose_name_plural = verbose_name
