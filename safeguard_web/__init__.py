import pymysql

pymysql.install_as_MySQLdb()

# 确保 Celery app 在 Django 启动时加载
from safeguard_web.celery import app as celery_app

__all__ = ("celery_app",)
