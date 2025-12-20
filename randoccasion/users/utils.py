__all__ = ()

import asyncio

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from telegram import Bot

from randoccasion.settings import TELEGRAM_BOT_TOKEN
from users.models import ActivationToken, User


def send_activation_email(self, user):
    activation_token = ActivationToken.create_for_user(user)

    activate_link = self.request.build_absolute_uri(
        reverse(
            "users:activate",
            kwargs={"token": activation_token.token},
        ),
    )

    send_mail(
        subject=_("Активация профиля на сайте"),
        message=_(
            "Здравствуйте, {username}!\n\n"
            "Для активации вашего аккаунта перейдите по ссылке:\n"
            "{activate_link}\n\n"
            "Ссылка действительна {hours} часа.\n\n"
            "Если вы не регистрировались, проигнорируйте это письмо.",
        ).format(
            username=user.username,
            activate_link=activate_link,
            hours=24,
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


async def send_tg_message(tg_id, message):
    bot = Bot(TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=tg_id, text=message, parse_mode="HTML")
    except Exception:
        pass


def send_tg_message_sync(tg_id, message):
    return asyncio.run(send_tg_message(tg_id, message))


def q_search(query):
    if query.isdigit():
        return User.objects.filter(id=query)

    if "@" in query:
        user = User.objects.by_mail(query)
        if user:
            return User.objects.filter(id=user.id)

        return User.objects.none()

    keywords = [word for word in query.split() if word]

    q_objects = Q()

    for token in keywords:
        q_objects |= Q(username__icontains=token)
        q_objects |= Q(first_name__icontains=token)
        q_objects |= Q(last_name__icontains=token)
        q_objects |= Q(email__icontains=token)
        q_objects |= Q(profile__interests__name__icontains=token)

    return User.objects.filter(q_objects).distinct()
