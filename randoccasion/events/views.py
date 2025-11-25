__all__ = ()

from django.shortcuts import render

from events.models import Event


def all_events(request):
    template_name = "events/events.html"
    context = {
        "events": Event.objects.is_active(),
    }
    return render(request, template_name, context)
