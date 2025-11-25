__all__ = ()

import sys

from django.contrib.auth.models import (
    AbstractUser,
    UserManager as DjangoUserManager,
)
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


if "makemigrations" not in sys.argv and "migrate" not in sys.argv:
    User._meta.get_field("email")._unique = True


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
