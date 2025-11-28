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

    def availaible_participants(self):
        return F("max_participants") - 1 - self.participants.count()

    def expired(self):
        return self.filter(
            Q(expires_at__lte=timezone.now()) | Q(is_active=False),
        )
