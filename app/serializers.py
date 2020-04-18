from .models import ItemRequest, Accepts, Organizations, AreasCatered
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

class AreasCateredSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreasCatered
        fields = "__all__"