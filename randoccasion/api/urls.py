from django.urls import path

from api.views import (
    EventDetail,
    EventListCreate,
    InterestDetail,
    InterestListCreate,
    UserDetail,
    UserListCreate,
)

urlpatterns = [
    path("users/", UserListCreate.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetail.as_view(), name="user-detail"),
    path("events/", EventListCreate.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetail.as_view(), name="event-detail"),
    path("interests/", InterestListCreate.as_view(), name="interest-list"),
    path(
        "interests/<int:pk>/",
        InterestDetail.as_view(),
        name="interest-detail",
    ),
]
