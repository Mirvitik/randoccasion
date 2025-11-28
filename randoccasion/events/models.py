__all__ = ()

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from events.managers import EventManager
from users.models import User


class Event(models.Model):
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
        default="Без темы",
    )
    who_can_see = models.CharField(
        verbose_name="Кто может видеть публикацию",
        choices=WHO_CAN_SEE_CHOICES,
        default=WHO_CAN_SEE_CHOICES[0],
    )
    slug = models.SlugField(unique=True)
    description = CKEditor5Field("Описание", blank=True)
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
        verbose_name="Участники",
    )
    max_participants = models.PositiveSmallIntegerField(
        verbose_name=_("Максимальное количество участников"),
        default=1,
    )
    location = models.CharField(
        verbose_name=_("Примерное местоположение, город"),
        default="Не указано",
    )
    created_at = models.DateTimeField(
        verbose_name=_("Создано"),
        auto_now_add=True,
        null=True,
    )
    expires_at = models.DateTimeField(
        verbose_name=_("Истекает через (не ранее 15мин с этого момента)"),
        default=timezone.now() + timezone.timedelta(hours=3),
        validators=[
            MinValueValidator(timezone.now() + timezone.timedelta(minutes=15)),
        ],
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
