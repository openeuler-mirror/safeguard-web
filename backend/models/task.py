"""Task 任务模型"""
from django.db import models


class Task(models.Model):
    """独立任务模型，支持各类异步操作的追踪"""

    STATUS_CHOICES = [
        ("pending", "等待中"),
        ("running", "运行中"),
        ("success", "成功"),
        ("failed", "失败"),
    ]

    TYPE_CHOICES = [
        ("os_install", "系统安装"),
        ("os_migrate", "系统迁移"),
        ("safeguard_deploy", "安全部署"),
        ("safeguard_rollback", "安全回滚"),
        ("hardware_collect", "硬件信息采集"),
        ("repo_sync", "仓库同步"),
    ]

    job_id = models.CharField(max_length=100, unique=True, verbose_name="任务ID")
    job_type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name="任务类型")
    target = models.CharField(max_length=255, verbose_name="目标")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="状态"
    )
    progress = models.IntegerField(default=0, verbose_name="进度百分比")
    result = models.JSONField(default=dict, blank=True, verbose_name="结果详情")
    error_message = models.TextField(blank=True, verbose_name="错误信息")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_id} - {self.status}"

    class Meta:
        db_table = "task"
        ordering = ["-created_at"]
        verbose_name = "任务"
        verbose_name_plural = verbose_name