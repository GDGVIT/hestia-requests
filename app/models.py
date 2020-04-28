from django.db import models

# Create your models here.
class ItemRequest(models.Model):
    request_made_by = models.CharField(max_length=255)
    item_name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    description = models.CharField(max_length=250, null=True, default=None)
    date_time_created = models.DateTimeField(auto_now_add=True)
    accepted_by = models.CharField(max_length=1000, default='')

    class Meta:
        ordering = ['-date_time']

class Accepts(models.Model):
    request_made_by = models.CharField(max_length=255)
    request_acceptor = models.CharField(max_length=255)
    request_id = models.CharField(max_length=500)
    item_names = models.CharField(max_length=10000)

class Organizations(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    email = models.EmailField()
    phone_no = models.CharField(max_length=10)
    address = models.CharField(max_length=250, null=True, default=None)
    other_contact = models.CharField(max_length=250, null=True, default=None)
    web_links = models.CharField(max_length=250, null=True, default=None)
    is_verified = models.BooleanField(default=False)

class AreasCatered(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    org_id = models.ForeignKey(Organizations, on_delete=models.CASCADE)

