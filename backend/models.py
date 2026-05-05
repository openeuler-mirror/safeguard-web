import uuid

from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class UsersManager(BaseUserManager):
    """用户管理器"""
    def create_user(self, user, password=None, **extra_fields):
        if not user:
            raise ValueError('用户名校验')
        user = self.model(user=user, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user, password=None, **extra_fields):
        extra_fields.setdefault('enable', 1)
        return self.create_user(user, password, **extra_fields)


class Users(AbstractBaseUser):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="用户UUID")
    user = models.CharField(max_length=50, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=128)  # AbstractBaseUser要求
    nickname = models.CharField(max_length=50, default="系统用户", verbose_name="昵称")
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="手机号")
    email = models.EmailField(blank=True, default="", verbose_name="邮箱")
    enable = models.IntegerField(default=1, verbose_name="是否启用 1=正常 2=冻结")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Django auth必需字段
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'user'

    class Meta:
        db_table = "users"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    objects = UsersManager()

    def __str__(self):
        return self.user

    def set_password(self, raw_password):
        self.password = make_password(raw_password)


class Cluster(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

