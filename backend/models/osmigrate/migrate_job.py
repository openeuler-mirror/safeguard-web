"""OSmigrate 迁移任务模型"""
from django.db import models


class MigrateJob(models.Model):
    """系统迁移任务模型"""

    MIGRATE_TYPE_CHOICES = [
        ("iaas", "IaaS"),
        ("yunguan", "云管"),
    ]

    STATUS_CHOICES = [
        ("pending", "等待中"),
        ("running", "运行中"),
        ("success", "成功"),
        ("failed", "失败"),
        ("rebooting", "重启中"),
    ]

    PHASE_CHOICES = [
        ("init", "初始化"),
        ("migrate", "迁移执行"),
        ("migrate_back", "迁移回滚"),
        ("post", "后置处理"),
    ]

    job_id = models.CharField(max_length=100, unique=True, verbose_name="任务ID")
    job_type = models.CharField(max_length=50, choices=PHASE_CHOICES, verbose_name="任务阶段")
    migrate_type = models.CharField(max_length=20, choices=MIGRATE_TYPE_CHOICES, blank=True, verbose_name="迁移类型")
    target_host = models.CharField(max_length=255, verbose_name="目标主机")
    hosts_json = models.JSONField(default=list, blank=True, verbose_name="多主机列表")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="状态")
    progress = models.IntegerField(default=0, verbose_name="进度百分比")
    result = models.JSONField(default=dict, blank=True, verbose_name="结果详情")
    error_message = models.TextField(blank=True, verbose_name="错误信息")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_id} - {self.status}"

    class Meta:
        db_table = "migrate_job"
        ordering = ["-created_at"]
        verbose_name = "迁移任务"
        verbose_name_plural = verbose_name
