__all__ = ()

from rest_framework import serializers

from events.models import Event, Interest
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
        )


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "topic",
            "who_can_see",
            "image",
            "slug",
            "description",
            "is_active",
            "max_participants",
            "location",
            "latitude",
            "longitude",
            "expires_at",
            "creator",
            "participants",
            "interests",
        )


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = "__all__"
