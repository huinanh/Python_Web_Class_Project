# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.
class Record(models.Model):
    UserID = models.CharField(max_length=10)
    Time = models.IntegerField()
