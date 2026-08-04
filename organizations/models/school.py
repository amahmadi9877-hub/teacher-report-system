from django.db import models


# Create your models here.
class School(models.Model):
    name = models.CharField(max_length=250)
    manager = models.CharField(max_length=150, blank=True, null=True)
    business_phone = models.CharField(max_length=14, unique=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
