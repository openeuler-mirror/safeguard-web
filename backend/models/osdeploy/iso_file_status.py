from django.db import models


class ISOFileStatus(models.Model):
    """ISO文件状态"""

    STATUS_CHOICES = [
        ("available", "可用"),
        ("uploading", "上传中"),
        ("error", "错误"),
        ("disabled", "禁用"),
    ]

    filename = models.CharField(max_length=255, unique=True, verbose_name="文件名")
    size = models.BigIntegerField(verbose_name="文件大小(字节)")
    md5sum = models.CharField(max_length=32, verbose_name="MD5校验")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available", verbose_name="状态")
    file_path = models.CharField(max_length=500, blank=True, verbose_name="文件路径")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.filename

    class Meta:
        db_table = "iso_file_status"
        ordering = ['id']
        verbose_name = "ISO文件状态"
        verbose_name_plural = verbose_name