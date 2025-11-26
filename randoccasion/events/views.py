__all__ = ()

from django.shortcuts import render
from django.views.generic import DetailView

from events.models import Event


def all_events(request):
    template_name = "events/events.html"
    context = {
        "events": Event.objects.is_active(),
    }
    return render(request, template_name, context)


class EventDetailView(DetailView):
    template_name = "events/eventinfo.html"
    queryset = Event.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        context["event"] = event

        return context
