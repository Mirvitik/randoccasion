__all__ = ()


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

from api.forms import APICreateForm
from api.serializers import (
    EventSerializer,
    InterestSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserSerializer,
)
from events.models import Event
from users.models import Interest, User


class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (HasAPIKey,)


class RegisterView(generics.CreateAPIView):
    permission_classes = (HasAPIKey,)
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        response.data = {
            "message": "User was created. Check email.",
            "user_id": response.data.get("id"),
            "username": response.data.get("username"),
        }
        return response


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            login(request, user)

            return Response(
                {
                    "message": "Успешный вход",
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (HasAPIKey,)


class EventListCreate(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (HasAPIKey,)


class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (HasAPIKey,)


class InterestListCreate(generics.ListCreateAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = (HasAPIKey,)


class InterestDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = (HasAPIKey,)


@method_decorator(staff_member_required, name="dispatch")
class APIKeyCreate(LoginRequiredMixin, FormView):
    form_class = APICreateForm
    template_name = "api/apicreate.html"
    success_url = reverse_lazy("api:apikey-create")

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        expiry_date = form.cleaned_data["expiry_date"]
        _, key = APIKey.objects.create_key(name=name, expiry_date=expiry_date)

        self.request.session["key"] = key
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "key" in self.request.session:
            context["key"] = self.request.session["key"]

        self.request.session["key"] = None
        return context
