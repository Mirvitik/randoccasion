__all__ = ()

from django.views.generic import DetailView, ListView

from events.models import Event
from events.utils import q_search


class EventIndexView(ListView):
    template_name = "events/events.html"
    context_object_name = "events"
    queryset = Event.objects.all()
    paginate_by = 100

    def get_queryset(self):
        query = self.request.GET.get("q")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        only_active = self.request.GET.get("only_active")
        sort_published = self.request.GET.get("sort_published")
        sort_expiry = self.request.GET.get("sort_expiry")
        sort_alphabet = self.request.GET.get("sort_alpha")

        if only_active:
            events = Event.objects.is_active()
        else:
            events = super().get_queryset()

        if query:
            events = q_search(query)

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
            ordering.append("created_at")
        elif sort_expiry == "asc":
            ordering.append("-created_at")

        if sort_alphabet == "desc":
            ordering.append("-name")
        elif sort_alphabet == "asc":
            ordering.append("name")

        if len(ordering) > 0:
            events.order_by(*ordering)

        return events

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class EventDetailView(DetailView):
    template_name = "events/eventinfo.html"
    queryset = Event.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        context["event"] = event

        return context
