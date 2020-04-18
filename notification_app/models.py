from django.db import models

# Create your models here.
class UserFCMDevice(models.Model):

    user_id = models.CharField(max_length=255)
    registration_id = models.TextField()
    date_time_created = models.DateTimeField(auto_now_add=True)
