__all__ = ()

import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from events.models import Event, Interest
from users.models import User
from users.utils import send_activation_email


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
        read_only_fields = fields


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=True,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "password_confirm")
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Пароли не совпадают"},
            )

        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            is_active=False,
        )

        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("Request не найден в контексте")

        send_activation_email(user, request)

        return user


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            try:
                formatik, imgstr = data.split(";base64,")
                ext = formatik.split("/")[-1]
                data = base64.b64decode(imgstr)
                file_name = f"{uuid.uuid4()}.{ext}"
                data = ContentFile(data, name=file_name)
            except Exception as e:
                raise serializers.ValidationError(
                    f"Некорректный формат base64 изображения: {str(e)}",
                )

        return super().to_internal_value(data)


class EventSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)
    image = Base64ImageField(
        required=False,
        allow_null=True,
        allow_empty_file=True,
        max_length=None,
    )

    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "topic",
            "image",
            "slug",
            "description",
            "is_active",
            "max_participants",
            "location",
            "latitude",
            "longitude",
            "expires_at",
            "creator_id",
            "interests",
        )


class InterestSerializer(serializers.ModelSerializer):
    permission_classes = (IsAuthenticated,)

    class Meta:
        model = Interest
        fields = "__all__"
