from django.db import models

class hosts(models.Model):
    ipaddress = models.CharField(max_length=50)
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    port = models.IntegerField(null=True, blank=True)
    cluster = models.CharField(max_length=50)

class users(models.Model):
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

class cluster(models.Model):
    name = models.CharField(max_length=50)

