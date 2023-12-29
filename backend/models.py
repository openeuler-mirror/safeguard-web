from django.db import models

class hosts(models.Model):
    ipaddress = models.CharField(max_length=50)
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    port = models.IntegerField(null=True, blank=True)
    cluster = models.CharField(max_length=50)
    def __str__(self):
        return self.ipaddress
    

class users(models.Model):
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    def __str__(self):
        return self.user

class cluster(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

