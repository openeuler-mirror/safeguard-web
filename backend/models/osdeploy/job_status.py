from django.db import models


class JobStatus(models.Model):
    """任务状态"""

    STATUS_CHOICES = [
        ("pending", "等待中"),
        ("running", "运行中"),
        ("success", "成功"),
        ("failed", "失败"),
    ]

    JOB_TYPE_CHOICES = [
        ("os_install", "系统安装"),
        ("os_migrate", "系统迁移"),
        ("hardware_collect", "硬件信息采集"),
    ]

    job_id = models.CharField(max_length=100, unique=True, verbose_name="任务ID")
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, verbose_name="任务类型")
    target = models.CharField(max_length=255, verbose_name="目标")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="状态")
    progress = models.IntegerField(default=0, verbose_name="进度百分比")
    result = models.JSONField(default=dict, blank=True, verbose_name="结果详情")
    error_message = models.TextField(blank=True, verbose_name="错误信息")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_id} - {self.status}"

    class Meta:
        db_table = "job_status"
        ordering = ['-created_at']
        verbose_name = "任务状态"
        verbose_name_plural = verbose_name