from django.urls import path

from api.views import (
    APIKeyCreate,
    EventDetail,
    EventListCreate,
    InterestDetail,
    InterestListCreate,
    RegisterView,
    UserDetail,
    UserListCreate,
)

app_name = "api"

urlpatterns = [
    path("users/", UserListCreate.as_view(), name="user-list"),
    path("register/", RegisterView.as_view(), name="register"),
    path("users/<int:pk>/", UserDetail.as_view(), name="user-detail"),
    path("events/", EventListCreate.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetail.as_view(), name="event-detail"),
    path("interests/", InterestListCreate.as_view(), name="interest-list"),
    path(
        "interests/<int:pk>/",
        InterestDetail.as_view(),
        name="interest-detail",
    ),
    path(
        "apikey-create/",
        APIKeyCreate.as_view(),
        name="apikey-create",
    ),
]
