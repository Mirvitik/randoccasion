__all__ = ()

from django.db.models import Count, F, Manager
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

    def recommended_events_for_user(self, user):
        user_interests = user.profile.interests.all()
        if not user_interests.exists():
            return self.none()

        queryset = self.get_queryset()

        queryset = queryset.filter(
            interests__in=user_interests,
            is_active=True,
            expires_at__gt=timezone.now(),
        )

        queryset = queryset.annotate(num_participants=Count("participants"))
        queryset = queryset.filter(num_participants__lt=F("max_participants"))
        queryset = queryset.distinct()

        return queryset
