"""Celery 配置"""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "safeguard_web.settings")

app = Celery("safeguard_web")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
