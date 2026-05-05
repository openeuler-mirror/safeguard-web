import uuid

from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone

class Hosts(models.Model):
    ipaddress = models.CharField(max_length=50)
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    port = models.IntegerField(null=True, blank=True)
    cluster = models.CharField(max_length=50)

    def __str__(self):
        return self.ipaddress


class Users(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="用户UUID")
    user = models.CharField(max_length=50, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50, default="系统用户", verbose_name="昵称")
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="手机号")
    email = models.EmailField(blank=True, default="", verbose_name="邮箱")
    enable = models.IntegerField(default=1, verbose_name="是否启用 1=正常 2=冻结")
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


class Cluster(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

