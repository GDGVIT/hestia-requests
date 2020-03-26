from django.db import models

# Create your models here.
class ItemRequest(models.Model):
    request_made_by = models.CharField(max_length=255)
    item_name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    date_time_created = models.DateTimeField(auto_now_add=True)

class Accepts(models.Model):
    request_made_by = models.CharField(max_length=255)
    request_acceptor = models.CharField(max_length=255)
    request_id = models.ForeignKey(ItemRequest, on_delete=models.CASCADE)

