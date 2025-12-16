__all__ = ()

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from sorl.thumbnail import get_thumbnail

from events.managers import EventManager
from users.models import Interest, User


def default_expires_at():
    return timezone.now() + timezone.timedelta(hours=3)


def min_expires_at():
    return timezone.now() + timezone.timedelta(minutes=15)


class Event(models.Model):
    def get_upload_path(self, filename):
        return f"uploads_events/{self.id}/{filename}"

    WHO_CAN_SEE_CHOICES = [
        ("all", _("Все")),
        ("only_friends", _("Только друзья")),
        ("only_for_me", _("Только я")),
    ]
    name = models.CharField(
        verbose_name=_("Событие"),
        max_length=200,
        default=_("Без названия"),
    )
    topic = models.CharField(
        verbose_name=_("Тема события"),
        default=_("Без темы"),
    )
    who_can_see = models.CharField(
        verbose_name=_("Кто может видеть публикацию"),
        choices=WHO_CAN_SEE_CHOICES,
        default=WHO_CAN_SEE_CHOICES[0],
    )
    image = models.ImageField(
        verbose_name=_("картинка"),
        upload_to=get_upload_path,
        null=True,
        blank=True,
    )
    slug = models.SlugField(unique=True)
    description = CKEditor5Field(_("Описание"), blank=True)
    is_active = models.BooleanField(verbose_name=_("Активно"), default=True)
    creator = models.ForeignKey(
        to=User,
        related_name="events",
        on_delete=models.CASCADE,
        null=True,
    )
    participants = models.ManyToManyField(
        User,
        blank=True,
        related_name="events_participating",
        verbose_name=_("Участники"),
    )
    max_participants = models.PositiveSmallIntegerField(
        verbose_name=_("Максимальное количество участников"),
        default=1,
    )
    location = models.CharField(
        verbose_name=_("Примерное местоположение, город"),
        default=_("Не указано"),
    )
    latitude = models.FloatField(
        verbose_name=_("Широта"),
        blank=True,
        null=True,
    )
    longitude = models.FloatField(
        verbose_name=_("Долгота"),
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        verbose_name=_("Создано"),
        auto_now_add=True,
        null=True,
    )
    expires_at = models.DateTimeField(
        verbose_name=_("Истекает через (не ранее 15мин с этого момента)"),
        default=default_expires_at,
        validators=[
            MinValueValidator(min_expires_at),
        ],
    )
    interests = models.ManyToManyField(
        Interest,
        blank=True,
        related_name="events",
        verbose_name=_("Интересы"),
    )

    objects = EventManager()

    class Meta:
        db_table = "event"
        indexes = [
            models.Index(fields=["expires_at"]),
            models.Index(fields=["topic", "is_active"]),
        ]
        ordering = ["created_at"]
        verbose_name = _("Событие")
        verbose_name_plural = _("События")

    def expires_after(self):
        tot_seconds = (self.expires_at - timezone.now()).total_seconds()

        if tot_seconds <= 0:
            return -1

        days = int(tot_seconds // 86400)
        hours = int((tot_seconds % 86400) // 3600)
        minutes = int((tot_seconds % 3600) // 60)

        if days > 0:
            return f"{days} д. {hours} ч."

        if hours > 0:
            return f"{hours} ч. {minutes} мин."

        return f"{minutes} мин."

    def get_image_300x300(self):
        if self.image:
            return get_thumbnail(
                self.image,
                "300x300",
                crop="center",
                quality=99,
            )

        return None

    def available_slots(self):
        return self.max_participants - self.participants.count()

    def is_full(self):
        return self.participants.count() >= self.max_participants

    def can_join(self, user):
        if (
            not user.is_authenticated
            or self.creator == user
            or not self.is_active
            or self.expires_at <= timezone.now()
        ):
            return False

        return (
            not self.is_full()
            and not self.participants.filter(id=user.id).exists()
        )

    def pending_requests_count(self):
        return self.requests.filter(status="pending").count()


class EventRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", _("В ожидании")),
        ("accepted", _("Принят")),
        ("rejected", _("Отклонен")),
    ]

    event = models.ForeignKey(
        Event,
        related_name="requests",
        on_delete=models.CASCADE,
        verbose_name=_("Событие"),
    )
    user = models.ForeignKey(
        User,
        related_name="event_requests",
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Статус"),
    )
    message = models.TextField(
        verbose_name=_("Сообщение"),
        blank=True,
        max_length=500,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Создано"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Обновлено"),
    )

    class Meta:
        db_table = "event_request"
        constraints = [
            models.constraints.UniqueConstraint(
                fields=("event", "user"),
                name="unique_constraint_event_user",
            ),
        ]
        ordering = ["-created_at"]
        verbose_name = _("Запрос на событие")
        verbose_name_plural = _("Запросы на события")

    def __str__(self):
        return f"{self.user.username} -> {self.event.name} [{self.status}]"
