from django.urls import include, path

from core.views import HealthView

urlpatterns = [
    path("api/health/", HealthView.as_view(), name="health"),
    path("api/auth/", include("accounts.urls")),
    path("api/kits/", include("transitions.urls")),
]
