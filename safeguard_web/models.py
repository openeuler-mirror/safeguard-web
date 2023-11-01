from django.db import models

# Create your models here.
class Host(models.Model):
    hostname = models.CharField(max_length=100, primary_key=True)
    ip = models.CharField(max_length=16)
    
    def __str__(self):
        return self.hostname