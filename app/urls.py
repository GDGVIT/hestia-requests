from django.urls import include, path
from rest_framework import routers

from .views import (
    ItemRequestView,
    AllRequestView,
    AcceptsView
)

router = routers.DefaultRouter()


urlpatterns = [
    path(
        'item_requests/',
        ItemRequestView.as_view()
    ),
    path(
        'item_requests/<int:pk>/',
        ItemRequestView.as_view()
    ),
    path(
        'view_all_item_requests/',
        AllRequestView.as_view()
    ),
    path(
        'accept/',
        AcceptsView.as_view()
    )

]