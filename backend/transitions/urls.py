from django.urls import path

from transitions.views import (
    ItemProgressView,
    ItemThreadView,
    KitDetailView,
    KitListCreateView,
    PlaybookGenerateView,
    ReadinessCheckView,
    SignOffView,
)

urlpatterns = [
    path("", KitListCreateView.as_view(), name="kit-list-create"),
    path("playbook/generate/", PlaybookGenerateView.as_view(), name="playbook-generate"),
    path("<str:kit_id>/", KitDetailView.as_view(), name="kit-detail"),
    path("<str:kit_id>/items/<str:item_id>/progress/", ItemProgressView.as_view(), name="item-progress"),
    path("<str:kit_id>/items/<str:item_id>/thread/", ItemThreadView.as_view(), name="item-thread"),
    path("<str:kit_id>/readiness-check/", ReadinessCheckView.as_view(), name="readiness-check"),
    path("<str:kit_id>/sign-off/", SignOffView.as_view(), name="sign-off"),
]
