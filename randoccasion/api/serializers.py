__all__ = ()

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework import serializers

from events.models import Event, Interest
from users.models import ActivationToken, User


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

        self.send_activation_email(user, request)

        return user

    def send_activation_email(self, user, request):
        activation_token = ActivationToken.create_for_user(user)

        activate_link = request.build_absolute_uri(
            reverse(
                "users:activate",
                kwargs={"token": activation_token.token},
            ),
        )

        send_mail(
            subject="Активация профиля на сайте",
            message=f"""
                       Здравствуйте, {user.username}!

                       Для активации вашего аккаунта перейдите по ссылке:
                       {activate_link}

                       Ссылка действительна 24 часа.
                       """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
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
