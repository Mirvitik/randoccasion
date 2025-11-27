__all__ = ()

from django.views.generic import DetailView, ListView

from events.models import Event
from events.utils import q_search


class EventIndexView(ListView):
    template_name = "events/events.html"
    context_object_name = "events"
    queryset = Event.objects.is_active()

    def get_queryset(self):
        query = self.request.GET.get("q")

        if query:
            return q_search(query)

        return super().get_queryset()

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
