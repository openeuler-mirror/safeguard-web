from django.db import models
from backend.models.osdeploy.repo_status import RepoStatus


class KickStartFileStatus(models.Model):
    """Kickstart文件状态"""

    name = models.CharField(max_length=100, unique=True, verbose_name="模板名称")
    content = models.TextField(verbose_name="模板内容")
    repo = models.ForeignKey(
        RepoStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="关联仓库"
    )
    kernel_options = models.JSONField(default=dict, blank=True, verbose_name="内核参数")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "kickstart_file_status"
        ordering = ['id']
        verbose_name = "Kickstart文件状态"
        verbose_name_plural = verbose_name