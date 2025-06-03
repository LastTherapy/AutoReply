from django.db import models
from django.utils import timezone


class HHResume(models.Model):
    hh_id = models.CharField(max_length=50, unique=True),
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class HHVacancy(models.Model):
    hh_id = models.CharField(max_length=50, unique=True),
    name = models.CharField(max_length=200)

    