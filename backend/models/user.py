import uuid

from django.db import models
from django.contrib.auth.hashers import make_password


class Users(models.Model):
    """用户模型"""
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="用户UUID")
    user = models.CharField(max_length=50, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=128)
    nickname = models.CharField(max_length=50, default="系统用户", verbose_name="昵称")
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="手机号")
    email = models.EmailField(blank=True, default="", verbose_name="邮箱")
    enable = models.IntegerField(default=1, verbose_name="是否启用 1=正常 2=冻结")
    avatar = models.CharField(max_length=255, blank=True, default="", verbose_name="头像URL")
    theme = models.CharField(max_length=20, blank=True, default="light", verbose_name="主题偏好")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    @property
    def is_active(self):
        return self.enable == 1


class EmailVerification(models.Model):
    """邮箱验证码"""
    email = models.EmailField(verbose_name="邮箱", db_index=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True, verbose_name="关联用户")
    code = models.CharField(max_length=6, verbose_name="验证码")
    expires_at = models.DateTimeField(verbose_name="过期时间")
    used = models.BooleanField(default=False, verbose_name="是否已使用")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "email_verification"
        verbose_name = "邮箱验证"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['email', 'code', 'used'], name='idx_email_code_used'),
        ]

    def __str__(self):
        return f"{self.email} - {self.code}"
