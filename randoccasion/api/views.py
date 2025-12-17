__all__ = ()

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from rest_framework import generics
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

from api.forms import APICreateForm
from api.serializers import EventSerializer, InterestSerializer, UserSerializer
from events.models import Event
from users.models import Interest, User


class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (HasAPIKey,)


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
