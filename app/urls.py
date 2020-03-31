from django.urls import include, path
from rest_framework import routers

from .views import (
    ItemRequestView,
    AllRequestView,
    AcceptsView,
    MyRequestView,
    OrganizatonView,
    VerifyOrganizationView,
    AdminOrganizationView,
    UserViewOrganization,
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
    ),
    path(
        'my_requests/',
        MyRequestView.as_view()
    ),
    path(
        'add_organization/',
        OrganizatonView.as_view()
    ),
    path(
        'view_organization/<int:pk>/',
        OrganizatonView.as_view()
    ),
    path(
        'user_organization_view/',
        UserViewOrganization.as_view()
    ),
    path(
        'admin_organization_view/',
        AdminOrganizationView.as_view()
    ),
    path(
        'verify_organization/<int:pk>/',
        VerifyOrganizationView.as_view()
    )
]