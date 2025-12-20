__all__ = ()

import uuid

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, View

from events.forms import EventCreateForm
from events.models import Event, EventRequest
from events.utils import q_search
from users.models import User
from users.utils import send_tg_message_sync


class EventIndexView(ListView):
    template_name = "events/events.html"
    context_object_name = "events"
    queryset = Event.objects.filter(who_can_see="all")
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

        if only_active:
            events = Event.objects.is_active()
        else:
            events = Event.objects.all()

        if only_friends and cur_user.is_authenticated:
            friends = cur_user.friends.all()
            events = events.filter(
                Q(who_can_see="all", creator__in=friends)
                | Q(who_can_see="only_friends", creator__in=friends),
            ).exclude(creator=cur_user)
        elif not only_my:
            if cur_user.is_authenticated:
                events = events.filter(
                    Q(who_can_see="all")
                    | Q(who_can_see="only_friends", creator__in=cur_user.friends.all())
                    | Q(creator=cur_user)
                )
            else:
                events = events.filter(who_can_see="all")

        if only_my and cur_user.is_authenticated:
            events = events.filter(creator=cur_user)

        query = None
        for value in q_values:
            if value and value.strip():
                query = value.strip()
                break

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
            ordering.append("-expires_at")
        elif sort_expiry == "asc":
            ordering.append("expires_at")

        if sort_alphabet == "desc":
            ordering.append("-name")
        elif sort_alphabet == "asc":
            ordering.append("name")

        if not ordering:
            ordering = ["-created_at"]

        events = events.select_related('creator').prefetch_related(
            Prefetch(
                'participants',
                queryset=get_user_model().objects.select_related('profile')
            )
        ).order_by(*ordering)

        return events

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


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
            messages.warning(
                request,
                message=_(
                    "По какой-то из причин вы не можете участвовать: "
                    "нет свободных мест/вы уже участвуете/событие неактивно",
                ),
            )
            return redirect("events:event-detail", pk=event_id)

        existing = EventRequest.objects.filter(
            event=event,
            user=user,
        ).first()

        if existing:
            if existing.status == "pending":
                messages.info(request, _("Ваш запрос уже был отправлен"))
            elif existing.status == "rejected":
                messages.error(request, _("Ваш запрос был отклонен"))
            else:
                messages.info(request, _("Запрос уже обработан"))
        else:
            message_text = request.POST.get("message", "")
            EventRequest.objects.create(
                event=event,
                user=user,
                message=message_text,
            )
            msg = (
                f"У Вас новая заявка на участие в событии "
                f"от {user.username}\n"
            )
            if user.last_name or user.last_name:
                msg += f"Имя: {request.user.last_name} {user.first_name}\n"
            else:
                msg += "Имя: не указано\n"

            if request.user.profile.birthday:
                msg += f"День рождения: {user.profile.birthday}\n"
            else:
                msg += "День рождения: не указан\n"

            msg += (
                "Сообщение от пользователя: <blockquote>"
                f"{message_text}</blockquote>\n"
            )
            msg += (
                f"Зайдите на https://{request.get_host()}/events/"
                "my-events-requests/\n"
                "для более детального осмотра анкеты"
            )
            user_to = User.objects.get(pk=event.creator_id)
            send_tg_message_sync(user_to.profile.telegram_id, msg)
            messages.success(
                request,
                _("Запрос на участие отправлен создателю события!"),
            )

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
            event.participants.add(event_request.user)
            user = User.objects.get(pk=event_request.user.id)
            msg = f"Ура! Вас приняли на событие {event.name}\n"
            send_tg_message_sync(user.profile.telegram_id, msg)
            messages.info(request, message="Заявка одобрена!")
            return redirect("events:my_events_requests")

        messages.warning(
            request,
            message=_("Достигнуто максимальное количество участников"),
        )
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
        messages.info(request, message=_("Заявка отклонена"))

        return redirect("events:my_events_requests")


class MyEventsView(LoginRequiredMixin, ListView):
    template_name = "events/my_events.html"
    context_object_name = "events"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        event_type = self.request.GET.get(
            "type",
            "created",
        )

        if event_type == "created":
            events = Event.objects.filter(creator=user)
        elif event_type == "participating":
            events = Event.objects.filter(participants=user).exclude(
                creator=user,
            )
        else:
            events = Event.objects.filter(
                Q(creator=user) | Q(participants=user),
            ).distinct()

        status = self.request.GET.get("status", "active")
        if status == "active":
            events = events.filter(
                is_active=True,
                expires_at__gt=timezone.now(),
            )
        elif status == "expired":
            events = events.filter(
                Q(is_active=False) | Q(expires_at__lte=timezone.now()),
            )

        sort_by = self.request.GET.get("sort_by", "-created_at")
        if sort_by in [
            "created_at",
            "-created_at",
            "expires_at",
            "-expires_at",
            "name",
            "-name",
        ]:
            events = events.order_by(sort_by)

        return events.select_related("creator").prefetch_related(
            "participants",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_type"] = self.request.GET.get("type", "created")
        context["current_status"] = self.request.GET.get("status", "active")
        context["current_sort"] = self.request.GET.get(
            "sort_by",
            "-created_at",
        )

        user = self.request.user
        context["created_count"] = Event.objects.filter(creator=user).count()
        context["participating_count"] = (
            Event.objects.filter(participants=user)
            .exclude(creator=user)
            .count()
        )
        context["active_count"] = (
            Event.objects.filter(
                Q(creator=user) | Q(participants=user),
                is_active=True,
                expires_at__gt=timezone.now(),
            )
            .distinct()
            .count()
        )

        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    form_class = EventCreateForm
    template_name = "events/create_event.html"
    success_url = reverse_lazy("events:my_events")

    def form_valid(self, form):
        event = form.save(commit=False)
        event.creator = self.request.user
        name = event.name if event.name != "Без названия" else "without-name"
        event.slug = f"{slugify(name)}-{uuid.uuid4().hex[:8]}"

        event.save()
        form.save_m2m()
        event.participants.add(self.request.user)

        messages.success(
            self.request,
            _("Событие успешно создано!"),
        )
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(
            self.request,
            _("Пожалуйста, исправьте ошибки в форме."),
        )
        return super().form_invalid(form)


class RecommendedEventsView(LoginRequiredMixin, ListView):
    template_name = "events/recommended_events.html"
    context_object_name = "events"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        return Event.objects.recommended_events_for_user(user)
