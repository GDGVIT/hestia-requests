from django.contrib import admin
from .models import ItemRequest, Accepts, Organizations, AreasCatered

# Register your models here.
admin.site.register(ItemRequest)
admin.site.register(Accepts)
admin.site.register(Organizations)
admin.site.register(AreasCatered)
