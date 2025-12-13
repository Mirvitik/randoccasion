__all__ = ()

from django.views.generic import ListView

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
            context["title"] = "Главная страница"
            context["user"] = self.request.user
            context["friends_count"] = self.request.user.friends.count()
        else:
            context["title"] = "Добро пожаловать"
            context["events_count"] = Event.objects.filter(
                is_active=True,
            ).count()

        return context
