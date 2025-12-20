from django.urls import path

from homepage.views import MainView, PrivacyView

app_name = "homepage"

urlpatterns = [
    path("", MainView.as_view(), name="main"),
    path("privacy/", PrivacyView.as_view(), name="privacy"),
]
