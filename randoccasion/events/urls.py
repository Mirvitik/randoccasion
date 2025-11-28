from django.urls import path

from events import views

app_name = "events"

urlpatterns = [
    path("", views.EventIndexView.as_view(), name="all_events"),
    path("<int:pk>/", views.EventDetailView.as_view(), name="event-detail"),
    path("event-request/<int:event_id>/", views.EventSendRequestView.as_view(), name="send_request_to_event"),
    path("my-events-requests/", views.MyEventsRequests.as_view(), name="my_events_requests"),
    path("event-request-accept/<int:request_id>/", views.EventAcceptRequestView.as_view(), name="accept_event_request"),
    path("event-request-reject/<int:request_id>/", views.EventRejectRequestView.as_view(), name="reject_event_request"),
]
