__all__ = ()

import sys

from django.contrib.auth.models import (
    AbstractUser,
    UserManager as DjangoUserManager,
)
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from sorl.thumbnail import get_thumbnail


class CustomUserManager(DjangoUserManager):
    def normalize_email(self, email):
        email = super().normalize_email(email)
        if not email:
            return ""

        email = email.lower().strip()
        if "@" not in email:
            return email

        try:
            local_part, domain = email.split("@", 1)

            if "+" in local_part:
                local_part = local_part.split("+")[0]

            yandex_domains = [
                "yandex.ru",
                "ya.ru",
                "yandex.ua",
                "yandex.com",
                "yandex.kz",
            ]

            if domain in yandex_domains:
                domain = "yandex.ru"
                local_part = local_part.replace(".", "-")

            elif domain == "gmail.com":
                local_part = local_part.replace(".", "")

            return f"{local_part}@{domain}"

        except (ValueError, AttributeError):
            return email

    def get_queryset(self):
        return super().get_queryset().select_related("profile")

    def active(self):
        return self.filter(is_active=True).select_related("profile")

    def by_mail(self, email):
        normalized_email = self.normalize_email(email)
        return self.active().filter(email=normalized_email).first()


class CustomUser(AbstractUser):
    attempts_count = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.username


class User(CustomUser):
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.email = User.objects.normalize_email(self.email)
        super().save(*args, **kwargs)

    class Meta:
        proxy = True

    def get_profile(self):
        return self.profile

    @property
    def friends(self):
        sent = Friendship.objects.filter(
            from_user=self,
            status="accepted",
        ).values_list("to_user", flat=True)

        received = Friendship.objects.filter(
            to_user=self,
            status="accepted",
        ).values_list("from_user", flat=True)

        return User.objects.filter(id__in=list(sent) + list(received))

    def is_friends_with(self, other_user):
        return other_user in self.friends

    def has_sent_request_to(self, other_user):
        return Friendship.objects.filter(
            from_user=self,
            to_user=other_user,
            status="pending",
        ).exists()

    def has_received_request_from(self, other_user):
        return Friendship.objects.filter(
            from_user=other_user,
            to_user=self,
            status="pending",
        ).exists()


if "makemigrations" not in sys.argv and "migrate" not in sys.argv:
    User._meta.get_field("email")._unique = True


class Interest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name = "Интерес"
        verbose_name_plural = "Интересы"

    def __str__(self):
        return self.name


class Profile(models.Model):
    def get_upload_path(self, filename):
        return f"uploads/{self.id}/{filename}"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("пользователь"),
    )
    birthday = models.DateField(
        verbose_name=_("день рождения"),
        null=True,
        blank=True,
    )
    image = models.ImageField(
        verbose_name=_("аватарка"),
        upload_to=get_upload_path,
        null=True,
        blank=True,
    )
    interests = models.ManyToManyField(
        Interest,
        verbose_name=_("интересы"),
        blank=True,
        related_name="profiles",
    )
    telegram_id = models.PositiveIntegerField(
        verbose_name=_("telegram_id"),
        blank=True,
        null=True,
    )
    tg_messages_cnt = models.PositiveIntegerField(
        verbose_name=_("Количество сообщений"),
        blank=True,
        default=0,
        validators=[MaxValueValidator(10)],
    )
    tg_last_message_date = models.DateTimeField(
        blank=True,
        null=True,
    )

    def get_image_300x300(self):
        if self.image:
            return get_thumbnail(
                self.image,
                "300x300",
                crop="center",
                quality=99,
            )

        return None

    class Meta:
        verbose_name = _("профиль")
        verbose_name_plural = _("профили")

    def __str__(self):
        return f"{self.user.username} - Профиль"


class Friendship(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friendships_sent",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friendships_received",
    )

    STATUS_CHOICES = (
        ("pending", "Ожидание"),
        ("accepted", "Принят"),
        ("rejected", "Отклонён"),
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")
        verbose_name = "Заявка в друзья"
        verbose_name_plural = "Заявки в друзья"

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({self.status})"
