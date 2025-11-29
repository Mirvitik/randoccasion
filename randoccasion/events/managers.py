__all__ = ()

from django.db.models import F, Manager, Q
from django.utils import timezone


class EventManager(Manager):
    def is_active(self):
        self.get_queryset().filter(
            is_active=True,
            expires_at__lte=timezone.now(),
        ).update(is_active=False)

        return self.get_queryset().filter(
            is_active=True,
            expires_at__gt=timezone.now(),
        )
