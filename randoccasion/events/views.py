__all__ = ()

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView, View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from events.models import Event, EventRequest
from events.utils import q_search


class EventIndexView(ListView):
    template_name = "events/events.html"
    context_object_name = "events"
    queryset = Event.objects.filter(who_can_see="all")
    paginate_by = 100

    def get_queryset(self):
        cur_user = self.request.user
        query = self.request.GET.get("q")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        only_active = self.request.GET.get("only_active")
        sort_published = self.request.GET.get("sort_published")
        sort_expiry = self.request.GET.get("sort_expiry")
        sort_alphabet = self.request.GET.get("sort_alpha")
        only_friends = self.request.GET.get("only_friends")
        only_my = self.request.GET.get("only_my")

        if only_active:
            events = Event.objects.is_active()
        else:
            events = super().get_queryset()
        
        if only_friends:
            friends = cur_user.friends
            events = events.filter(
                Q(who_can_see="all", creator__in=friends) |
                Q(who_can_see="only_friends", creator__in=friends)).exclude(creator=cur_user)
        
        if only_my:
            events = events.filter(creator=cur_user)

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

class EventSendRequestView(LoginRequiredMixin, View):
    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        user = request.user

        if not event.can_join(user):
            messages.warning(request, message="По какой-то из причин вы не можете участвовать: нет свободных мест/вы уже участвуете/событие неактивно")
            return redirect("events:event-detail", pk=event_id)

        existing = EventRequest.objects.filter(
            event=event,
            user=user,
        ).first()
        
        if existing:
            if existing.status == "pending":
                messages.info(request, "Ваш запрос уже был отправлен")
            elif existing.status == "rejected":
                messages.error(request, "Ваш запрос был отклонен")
            else:
                messages.info(request, "Запрос уже обработан")
        else:
            message_text = request.POST.get("message", "")
            EventRequest.objects.create(
                event=event,
                user=user,
                message=message_text,
            )
            messages.success(request, "Запрос на участие отправлен создателю события!")
        
        return redirect("events:event-detail", pk=event_id)

class MyEventsRequests(LoginRequiredMixin, ListView):
    template_name = "events/my_events_requests.html"
    context_object_name = "requests"
    paginate_by = 20

    def get_queryset(self):
        return EventRequest.objects.filter(
            event__creator=self.request.user,
        ).select_related("user", "event")


class EventAcceptRequestView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        event_request = get_object_or_404(
            EventRequest,
            id=request_id,
            event__creator=request.user,
            status="pending",
        )

        event = event_request.event

        if event.available_slots() > 0:
            event_request.status = "accepted"
            event_request.save()
            event.participants.add(request.user)
            messages.info(request, message="Заявка одобрена!")
            return redirect("events:my_events_requests")

        messages.warning(request, message="Достигнуто максимальное количество участников")
        return redirect("events:my_events_requests")

class EventRejectRequestView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        event_request = get_object_or_404(
            EventRequest,
            id=request_id,
            event__creator=request.user,
            status="pending",
        )

        event_request.status = "rejected"
        event_request.save()
        messages.info(request, message="Заявка отклонена")

        return redirect("events:my_events_requests")