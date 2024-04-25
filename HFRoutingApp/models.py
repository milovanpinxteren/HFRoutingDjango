from django.db import models

class Locations(models.Model):
    id = models.CharField(max_length=250, primary_key=True)
