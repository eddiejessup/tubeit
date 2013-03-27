from django.db import models

class Location(models.Model):
    long = models.FloatField()
    lat = models.FloatField()