"""Safeguard 部署记录模型"""
from django.db import models


class SafeguardDeploy(models.Model):
    """安全部署记录"""
    STATUS_CHOICES = [
        ("pending", "等待中"),
        ("running", "运行中"),
        ("success", "成功"),
        ("failed", "失败"),
    ]
    ARCH_CHOICES = [
        ("x86", "X86"),
        ("arm", "ARM"),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="部署名称")
    target_hosts = models.JSONField(default=list, verbose_name="目标主机列表")
    safeguard_type = models.CharField(max_length=50, default="safeguardx86", verbose_name="安全组件类型")
    arch = models.CharField(max_length=20, default="x86", choices=ARCH_CHOICES, verbose_name="架构")
    host = models.CharField(max_length=100, blank=True, verbose_name="目标主机IP")
    username = models.CharField(max_length=100, blank=True, verbose_name="用户名")
    password = models.CharField(max_length=100, blank=True, verbose_name="密码")
    port = models.CharField(max_length=10, default="22", verbose_name="端口")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="状态")
    result = models.JSONField(default=dict, blank=True, verbose_name="结果详情")
    error_message = models.TextField(blank=True, verbose_name="错误信息")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "safeguard_deploy"
        ordering = ["-created_at"]
        verbose_name = "Safeguard部署"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name} ({self.status})"