from django.db import models


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


class Host(models.Model):
    """宿主机"""
    hostname = models.CharField(max_length=255, verbose_name="主机名")
    ip_address = models.GenericIPAddressField(unique=True, verbose_name="管理IP")
    port = models.IntegerField(default=22, verbose_name="SSH端口")
    username = models.CharField(max_length=50, verbose_name="用户名")
    password = models.CharField(max_length=255, blank=True, verbose_name="密码（加密存储）")
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属集群")
    status = models.CharField(max_length=20, choices=[("online", "在线"), ("offline", "离线")], default="offline")
    os_type = models.CharField(max_length=50, blank=True, verbose_name="操作系统")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"

    class Meta:
        db_table = "hosts"
        ordering = ['id']
        verbose_name = "宿主机"
        verbose_name_plural = verbose_name


class VM(models.Model):
    """虚拟机"""
    STATUS_CHOICES = [
        ("stopped", "已停止"),
        ("running", "运行中"),
        ("paused", "暂停"),
        ("suspended", "挂起"),
    ]
    name = models.CharField(max_length=255, verbose_name="VM名称")
    uuid = models.CharField(max_length=100, unique=True, verbose_name="UUID")
    host = models.ForeignKey(Host, related_name="vms", on_delete=models.CASCADE, verbose_name="所属宿主机")
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属集群")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="stopped", verbose_name="状态")
    vcpu = models.IntegerField(default=1, verbose_name="虚拟CPU核数")
    memory = models.BigIntegerField(default=0, verbose_name="内存(字节)")
    disk = models.BigIntegerField(default=0, verbose_name="磁盘(字节)")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    mac_address = models.CharField(max_length=17, blank=True, verbose_name="MAC地址")
    os_type = models.CharField(max_length=50, blank=True, verbose_name="操作系统")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.ip_address or 'No IP'})"

    class Meta:
        db_table = "vms"
        ordering = ['id']
        verbose_name = "虚拟机"
        verbose_name_plural = verbose_name
