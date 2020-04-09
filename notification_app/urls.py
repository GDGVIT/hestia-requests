from django.urls import include, path
from rest_framework import routers

from .views import (
    FCMPushNotificationView,
    FCMRegisterDeviceView
)

router = routers.DefaultRouter()


urlpatterns = [
    path(
        'register_device/',
        FCMRegisterDeviceView.as_view()
    ),
    path(
        'send_notification/',
        FCMPushNotificationView.as_view()
    ),
]