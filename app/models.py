from django.db import models

# Create your models here.
class ItemRequest(models.Model):
    request_made_by = models.CharField(max_length=255)
    item_name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    date_time_created = models.DateTimeField(auto_now_add=True)
    accepted_by = models.CharField(max_length=1000, default='')

class Accepts(models.Model):
    request_made_by = models.CharField(max_length=255)
    request_acceptor = models.CharField(max_length=255)
    request_id = models.CharField(max_length=500)
    item_names = models.CharField(max_length=10000)

class Organizations(models.Model):
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    description = models.TextField()
    email = models.EmailField()
    phone_no = models.CharField(max_length=10)
    is_verified = models.BooleanField(default=False)

