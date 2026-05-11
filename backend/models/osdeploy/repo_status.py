from django.db import models


class RepoStatus(models.Model):
    """仓库状态"""

    REPO_TYPE_CHOICES = [
        ("yum", "YUM"),
        ("iso", "ISO"),
        ("http", "HTTP"),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="仓库名称")
    repo_type = models.CharField(max_length=20, choices=REPO_TYPE_CHOICES, verbose_name="仓库类型")
    base_url = models.URLField(verbose_name="仓库地址")
    is_default = models.BooleanField(default=False, verbose_name="是否默认")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "repo_status"
        ordering = ['id']
        verbose_name = "仓库状态"
        verbose_name_plural = verbose_name