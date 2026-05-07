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
    """集群分组"""
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
