__all__ = ()

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
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
from events.utils import q_search
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


class EventListCreate(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (HasAPIKey,)


class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (HasAPIKey,)


class InterestListCreate(generics.ListAPIView):
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


class EventSearchAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [HasAPIKey]
    paginate_by = 100

    def get_queryset(self):
        cur_user = self.request.user
        q_values = self.request.GET.getlist("q")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        only_active = self.request.GET.get("only_active")
        sort_published = self.request.GET.get("sort_published")
        sort_expiry = self.request.GET.get("sort_expiry")
        sort_alphabet = self.request.GET.get("sort_alpha")
        only_friends = self.request.GET.get("only_friends")
        only_my = self.request.GET.get("only_my")
        interest_id = self.request.GET.get("interest")

        if only_active:
            events = Event.objects.is_active()
        else:
            events = Event.objects.filter(who_can_see="all")

        if interest_id:
            events = events.filter(interests__id=interest_id)

        if only_friends and cur_user.is_authenticated:
            friends = cur_user.friends.all()
            events = events.filter(
                Q(who_can_see="all", creator__in=friends)
                | Q(who_can_see="only_friends", creator__in=friends),
            ).exclude(creator=cur_user)

        if only_my and cur_user.is_authenticated:
            events = events.filter(creator=cur_user)

        query = None
        for value in q_values:
            if value and value.strip():
                query = value.strip()
                break

        if query:
            try:

                return q_search(query)
            except ImportError:
                events = events.filter(
                    Q(name__icontains=query) | Q(description__icontains=query),
                )

        if date_from:
            events = events.filter(created_at__gte=date_from)

        if date_to:
            events = events.filter(created_at__lte=date_to)

        ordering = []

        if sort_published == "desc":
            ordering.append("-created_at")
        elif sort_published == "asc":
            ordering.append("created_at")

        if sort_expiry == "desc":
            ordering.append("-expires_at")
        elif sort_expiry == "asc":
            ordering.append("expires_at")

        if sort_alphabet == "desc":
            ordering.append("-name")
        elif sort_alphabet == "asc":
            ordering.append("name")

        if not ordering:
            ordering = ["-created_at"]

        return events.order_by(*ordering)
