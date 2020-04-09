from django.db import models

# Create your models here.
class UserFCMDevice(models.Model):

    user_id = models.CharField(max_length=255, unique=True)
    registration_id = models.TextField(unique=True)
