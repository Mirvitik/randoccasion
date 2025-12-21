__all__ = ()

from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, TemplateView

from events.models import Event


class MainView(ListView):
    model = Event
    context_object_name = "events"

    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ["homepage/main.html"]

        return ["homepage/guest_main.html"]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Event.objects.recommended_events_for_user(
                self.request.user,
            )[:6]

        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context["title"] = _("Главная страница")
            context["user"] = self.request.user
            context["friends_count"] = self.request.user.friends.count()
        else:
            context["title"] = _("Добро пожаловать")
            context["events_count"] = Event.objects.filter(
                is_active=True,
            ).count()

        return context


class PrivacyView(TemplateView):
    template_name = "homepage/privacy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = _("Конфиденциальность")
        context["user"] = self.request.user

        return context


class DocsView(TemplateView):
    template_name = "homepage/apidocs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = "API"
        context["user"] = self.request.user

        return context
