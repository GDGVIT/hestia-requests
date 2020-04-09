from .models import UserFCMDevice
from rest_framework import serializers

class UserFCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFCMDevice
        fields = "__all__"