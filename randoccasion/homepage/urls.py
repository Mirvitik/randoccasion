from django.urls import path

from homepage.views import DocsView, MainView, PrivacyView

app_name = "homepage"

urlpatterns = [
    path("", MainView.as_view(), name="main"),
    path("about-api/", DocsView.as_view(), name="about-api"),
    path("privacy/", PrivacyView.as_view(), name="privacy"),
]
