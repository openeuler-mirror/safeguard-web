from django.db import models


class LBMember(models.Model):
    """池成员"""

    pool = models.ForeignKey(
        "LBPool",
        related_name="members",
        on_delete=models.CASCADE,
        verbose_name="后端池"
    )
    address = models.GenericIPAddressField(verbose_name="IP地址")
    port = models.IntegerField(verbose_name="端口")
    weight = models.IntegerField(default=1, verbose_name="权重")
    is_enabled = models.BooleanField(default=True, verbose_name="是否启用")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address}:{self.port}"

    class Meta:
        db_table = "lb_member"
        ordering = ['-created_at']
        verbose_name = "池成员"
        verbose_name_plural = verbose_name