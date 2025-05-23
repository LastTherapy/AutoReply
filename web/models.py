from django.db import models
from django.utils import timezone


class HHUser(models.Model):
    hh_id = models.CharField(max_length=30, unique=True)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    expires_at = models.DateTimeField()

    def is_token_expired(self):
        return timezone.now() >= self.expires_at
