from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=20)
    token = models.CharField(max_length=200)
    refresh_token = models.CharField(max_length=200)
    update_time = models.DateTimeField(auto_now=True)

