from django.urls import path

from homepage.views import MainView

app_name = "homepage"

urlpatterns = [
    path("", MainView.as_view(), name="main"),
]
