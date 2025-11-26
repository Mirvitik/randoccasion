from django.urls import path

from events import views

app_name = "events"

urlpatterns = [
    path("", views.all_events, name="all_events"),
    path("<int:pk>/", views.EventDetailView.as_view(), name="event-detail"),
]
