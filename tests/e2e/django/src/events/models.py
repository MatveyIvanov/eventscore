from django.db import models


class EventModel(models.Model):
    uid = models.CharField(max_length=64)
    type = models.CharField(max_length=64)
    ts = models.CharField(max_length=32)
    payload = models.CharField(max_length=2056, null=True)


class EventLog(models.Model):
    data = models.CharField(max_length=2056)
    dt = models.DateTimeField()
