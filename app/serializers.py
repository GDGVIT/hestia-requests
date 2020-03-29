from .models import ItemRequest, Accepts, Organizations
from rest_framework import serializers

class ItemRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemRequest
        fields = "__all__"

class AcceptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accepts
        fields = "__all__"

class OrganizationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizations
        fields = "__all__"